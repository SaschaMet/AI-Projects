docker run -p 6333:6333 -p 6334:6334 --name qdrant -d \
    -v ./qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant