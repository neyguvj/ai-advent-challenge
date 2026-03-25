# AI Advent Challenge CLI

CLI client for interacting with the backend server.

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

### Create User

```bash
uv run cli_client.py user create \
    --base-url http://localhost:8080 \
    --email test@example.com \
    --password secret123
```

## Parameters

- `--base-url`: Base URL of the backend server (required for all commands)
- `--model`: Model ID to use (required for request command)
- `--temperature`: Model temperature (default: 0.1)
- `--prompt`: System prompt (default: empty)
- `--request`: User request (required for request command)
- `--email`: Email of the new user (required for user create command)
- `--password`: Password of the new user (required for user create command)
