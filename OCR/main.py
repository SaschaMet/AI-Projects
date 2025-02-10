import os
import json
import uvicorn
import pandas as pd
from pathlib import Path
from openai import OpenAI
from fastapi import FastAPI
from pydantic import BaseModel
from qdrant_client import QdrantClient

from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode


app = FastAPI()
qdrant_client = QdrantClient(url="http://host.docker.internal:6333")
openAI_client = OpenAI(
    base_url="http://host.docker.internal:1234/v1", api_key="lm-studio"
)

SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "product",
        "schema": {
            "type": "object",
            "properties": {
                "SKU": {"type": "string"},
                "Found": {"type": "boolean"},
            },
            "required": ["SKU", "Found"],
        },
    },
}


def query_qdrant():
    COLLECTION_NAME = "OCR-TEST"
    x = qdrant_client.scroll(
        collection_name=COLLECTION_NAME,
        limit=10,
        with_payload=True,
        with_vectors=False,
    )

    results = []
    for point in x[0]:
        results.append(point.payload)

    products = list(filter(lambda item: item["Type"] == "Product", results))
    orders = list(filter(lambda item: item["Type"] == "Order", results))

    return products, orders


def llm_call(json_table: str, ordered_product: str) -> str:
    completion = openAI_client.chat.completions.create(
        model="phi-4",
        messages=[
            {"role": "system", "content": "Extract the product information."},
            {
                "role": "user",
                "content": f"""Please check that the ordered product is in the following document.
                Here is the document:
                {json_table}

                Here it the ordered product:
                {ordered_product}

                The product information may differ, i.e. the SKU may be missing or the product name may be different. However, the price must be the same. If there is a product that almost matches the ordered product, please select it.

                Please return a JSON object with the SKU of the product ordered product and weather you found it or not. Here is an example:

                {{
                    "SKU": "123456", // this is the SKU of the ordered product
                    "Found": true // this is a boolean value indicating if the product was found in the document or not
                }}

                """,
            },
        ],
        response_format=SCHEMA,
        temperature=0.3,
        seed=42,
    )

    return json.loads(completion.choices[0].message.content)


@app.post("/process")
def process_file(data: dict):

    order_number = data["order_number"]
    tables = data["table"]

    products, orders = query_qdrant()

    order = list(filter(lambda item: item["OrderID"] == order_number, orders))[0]

    ordered_products = []

    for product_sku in order["Products"]:
        ordered_product = next(
            (product for product in products if product["SKU"] == product_sku), None
        )
        ordered_products.append(ordered_product)

    llm_responses = []

    for ordered_product in ordered_products:
        x = llm_call(tables, ordered_product)
        llm_responses.append(x)

    return llm_responses


class FileRequest(BaseModel):
    filepath: str


@app.post("/extract-table")
async def upload_file(request: FileRequest):
    try:
        print("Processing file: ", request.filepath)

        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = False
        pipeline_options.do_table_structure = True
        pipeline_options.table_structure_options.do_cell_matching = True
        pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE

        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=pipeline_options,
                )
            }
        )

        result = converter.convert(request.filepath)

        tables = ""
        for _, table in enumerate(result.document.tables):
            table_df: pd.DataFrame = table.export_to_dataframe()
            tables = tables + table_df.to_markdown() + "\n"

        return {"tables": tables}

    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8111, reload=True)
