#!/bin/bash
set -xe

# Assign arguments
BASE_URL="http://localhost:8080"
MODEL="Gigachat-2"
TEMPERATURE="0.1"
PROMPT="Ты дизайнер одежды для животных"
USER_REQUEST="Придумай три вида зимней одеждлы для кота"

# list available models
uv run --directory ../ client/cli_client.py list \
    --base-url "$BASE_URL"

# Run the CLI client with provided arguments
uv run --directory ../ client/cli_client.py request \
    --base-url "$BASE_URL" \
    --model "$MODEL" \
    --temperature "$TEMPERATURE" \
    --prompt "$PROMPT" \
    --request "$USER_REQUEST"

