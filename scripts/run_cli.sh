#!/bin/bash
set -e

# Assign arguments
BASE_URL="http://localhost:8080/api"
MODEL="Gigachat-2"
TEMPERATURE="0.1"
PROMPT="ты эксперт по разработке на языке программирования Go"
USER_REQUEST1="Сравни фреймворки для разработки веб приложений на Go.
- какие и для чего лучше подходят?
- на каких выше скорость разработки?
- какие лучше подходят для больших проектов?
"

USER_REQUEST2="Почему в языке Go не принято использовать ORM?"

USER_REQUEST3="Расскажи о паттернах параллельного программирования в Go. Приведи примеры и покажи, в каких ситуациях они применяются"

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

function run_llm() {
  echo "Running request..."
  uv run --directory ../ cli/cli_client.py request \
      --base-url="$BASE_URL" \
      --user="$USER"\
      --model="$MODEL" \
      --temperature="$TEMPERATURE" \
      --prompt="$PROMPT" \
      --request="$1"
  sleep 5
}

run_llm "$USER_REQUEST1"
run_llm "$USER_REQUEST2"
run_llm "$USER_REQUEST3"