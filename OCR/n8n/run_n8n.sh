docker volume create n8n_data_ocr

docker stop n8n_python || true
docker rm -f n8n_python || true

docker run -itd --name n8n_python -p 5678:5678 -v $(pwd)/data:/home/node/data docker.n8n.io/n8nio/n8n