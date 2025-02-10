"""
title: Search Order
author: Sascha Metzger
description: This tool can search for an order by email.
version: 0.0.1
"""

import asyncio
import requests
import logging

logging.basicConfig(level=logging.DEBUG)


class Tools:
    def __init__(self):
        self.api_url = (
            "http://host.docker.internal:6333/collections/CS-AGENT-TEST/points/query"
        )

    async def search_order_by_email(
        self,
        email: str,
        __event_emitter__=None,
    ) -> dict:
        """
        Search for orders based by email.

        :type string: The email to search for.
        :rtype: string: The order details.
        """

        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {"description": "Processing started...", "done": False},
                }
            )

        # Build the filter conditions
        must_conditions = []
        must_conditions.append({"key": "EMAIL", "match": {"value": email}})

        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"Processing search request using must conditions: {must_conditions}",
                        "done": False,
                    },
                }
            )

        await asyncio.sleep(2)

        payload = {
            "filter": {"must": must_conditions},
            "limit": 10,
            "with_payload": True,
        }

        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            response = response.json()
            response = response["result"]["points"][0]

            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"Processing completed. Got payload: {response}",
                            "done": True,
                        },
                    }
                )

            customer_name = response["payload"]["Customer Name"]
            email = response["payload"]["Email"]
            total_amount_net = response["payload"]["Total Amount Net"]
            total_amount_gross = response["payload"]["Total Amount Gross"]
            paid = response["payload"]["Paid"]
            order_date = response["payload"]["Order Date"]

            return f"""
Order Found:

Id: {id}
Customer Name: {customer_name}
Email: {email}
Total Amount Net: {total_amount_net}
Total Amount Gross: {total_amount_gross}
Paid: {paid}
Order Date: {order_date}
""".strip()

        except requests.RequestException as e:
            error_message = f"Error searching for order: {str(e)}"
            logging.debug(f"Error message:\n{error_message}")

            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "error",
                        "data": {"description": error_message, "done": True},
                    }
                )

            raise Exception(error_message)
