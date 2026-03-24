# AI Advent Challenge Client

CLI client for interacting with the backend server.

## Installation

```bash
# Install dependencies
pip install -e .
```

## Usage

### List Available Models

```bash
uv run cli_client.py list --base-url http://localhost:8080
```

### Run a Request

```bash
uv run cli_client.py request \
    --base-url http://localhost:5000 \
    --model ai-sage/GigaChat3-10B-A1.8B \
    --temperature 0.1 \
    --prompt "You are a helpful assistant." \
    --request "What is the capital of France?"
```

## Parameters

- `--base-url`: Base URL of the backend server (required for both commands)
- `--model`: Model ID to use (required for request command)
- `--temperature`: Model temperature (default: 0.1) 
- `--prompt`: System prompt (default: empty)
- `--request`: User request (required for request command)
