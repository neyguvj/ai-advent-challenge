from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from langchain_gigachat.chat_models import GigaChat
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Available models (this could be dynamic in a real implementation)
AVAILABLE_MODELS = [
    "Gigachat-2",
    "Gigachat-2-Pro",
    "Gigachat-2-Max",
]

DEFAULT_MODEL = AVAILABLE_MODELS[0]
DEFAULT_TEMPERATURE = 0.1
DEFAULT_MAX_TOKENS = 2048


def init_model(
    model=DEFAULT_MODEL, temperature=DEFAULT_TEMPERATURE, max_tokens=DEFAULT_MAX_TOKENS
):
    """Initialize the LLM model with given parameters"""
    api_key = os.environ.get("API_KEY")

    llm = GigaChat(
        credentials=api_key,
        model=model,
        scope="GIGACHAT_API_PERS",
        temperature=temperature,
        verify_ssl_certs=False,
        max_tokens=max_tokens,
    )

    return llm


def run_completion(llm, prompt, query):
    """Run the LLM completion with given parameters"""
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
            ("human", "{user_input}"),
        ]
    )

    chain = prompt_template | llm
    response = chain.invoke({"user_input": query})

    return response


@app.route("/list_models", methods=["GET"])
def list_models():
    """List all available models"""
    return jsonify({"models": AVAILABLE_MODELS})


@app.route("/completion", methods=["POST"])
def completion():
    """Send request to LLM and return response"""
    try:
        # Get parameters from the request
        data = request.get_json()

        model_id = data.get("model", DEFAULT_MODEL)
        prompt = data.get("prompt", "")
        user_request = data.get("request", "")
        temperature = data.get("temperature", DEFAULT_TEMPERATURE)
        max_tokens = data.get("max_tokens", DEFAULT_MAX_TOKENS)

        # Validate required parameters
        if not user_request:
            return jsonify({"error": "User request is required"}), 400

        # Initialize the model
        llm = init_model(model=model_id, temperature=temperature, max_tokens=max_tokens)

        # Run completion
        response = run_completion(llm, prompt, user_request)

        return jsonify(
            {
                "model": model_id,
                "prompt": prompt,
                "response": response.content,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
