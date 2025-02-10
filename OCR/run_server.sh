#!/bin/bash
docker build -t ocr_server .
docker stop ocr_server
docker rm -f ocr_server
docker run -d --name ocr_server -p 8111:8111 -v $(pwd)/data:/app/data ocr_server