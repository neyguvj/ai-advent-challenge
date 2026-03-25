#!/bin/bash
set -e

# Assign arguments
BASE_URL="http://localhost:8080/api"
MODEL="Gigachat-2"
TEMPERATURE="0.1"
PROMPT="Ты дизайнер одежды для животных"
USER_REQUEST1="Придумай три вида зимней одеждлы для кота"
USER_REQUEST2="Что мы придумывали в прошлом запросе?"
USER=test@example.com
PASSWORD="1234"

echo "Stopping services and cleanong..."
docker-compose -f ../docker/docker-compose.yaml down -v

echo "building and Starting services..."
docker-compose -f ../docker/docker-compose.yaml up -d --build --wait 

echo "Creating user..."
uv run --directory ../ cli/cli_client.py user create \
    --base-url="$BASE_URL" \
    --email="$USER" \
    --password="$PASSWORD"

echo "list available models..."
uv run --directory ../ cli/cli_client.py list \
    --base-url="$BASE_URL"

echo "Running first request..."
uv run --directory ../ cli/cli_client.py request \
    --base-url="$BASE_URL" \
    --user="$USER"\
    --model="$MODEL" \
    --temperature="$TEMPERATURE" \
    --prompt="$PROMPT" \
    --request="$USER_REQUEST1"

echo "Stopping services..."
docker-compose -f ../docker/docker-compose.yaml down

echo "Restarting services..."
docker-compose -f ../docker/docker-compose.yaml up -d --wait

echo "Running second request..."
uv run --directory ../ cli/cli_client.py request \
    --base-url="$BASE_URL" \
    --user="$USER"\
    --model="$MODEL" \
    --temperature="$TEMPERATURE" \
    --prompt="$PROMPT" \
    --request="$USER_REQUEST2"
