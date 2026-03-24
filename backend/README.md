# AI Advent Challenge Backend

Flask web server providing LLM completion services.

## Endpoints

### GET /list_models
List all available models.

**Response:**
```json
{
  "models": [
    "Gigachat-2",
    "Gigachat-2-Pro", 
    "Gigachat-2-Max"
  ]
}
```

### POST /completion
Send request to LLM and return response.

**Request Body:**
```json
{
  "model": "GigaChat-2",
  "prompt": "You are a helpful assistant...",
  "request": "What is the capital of France?",
  "temperature": 0.1,
  "max_tokens": 2048
}
```

**Response:**
```json
{
  "model": "GigaChat-2",
  "prompt": "You are a helpful assistant...",
  "request": "What is the capital of France?",
  "response": "The capital of France is Paris."
}
```

## Environment Variables

- `API_KEY` - API key for GigaChat

## Running the Server

```bash
# Go to Docker directory
```bash
cd ../docker
```

# Run the server
```bash
docker-compose up --build
```