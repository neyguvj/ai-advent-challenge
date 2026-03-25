from flask import Blueprint, request, jsonify
import os
from langchain_gigachat.chat_models import GigaChat
from langchain_core.prompts import ChatPromptTemplate
from app.routes.utils import run_request
from app.db.sessions import create_session, get_session_by_id
from app.db.messages import create_message, get_messages_by_session_id
from app.db.models import Role, Statistics
from app.db.statistics import update_statistics

# Available models (this could be dynamic in a real implementation)
AVAILABLE_MODELS = [
    "Gigachat-2",
    "Gigachat-2-Pro",
    "Gigachat-2-Max",
]

# https://developers.sber.ru/docs/ru/gigachat/tariffs/individual-tariffs
INPUT_PRICES = {
    "Gigachat-2": 1_300 / 20_000_000,
    "Gigachat-2-Pro": 1_500 / 3_000_000,
    "Gigachat-2-Max": 1_950 / 3_000_000,
}

OUTPUT_PRICES = {
    "Gigachat-2": 1_300 / 20_000_000,
    "Gigachat-2-Pro": 1_500 / 3_000_000,
    "Gigachat-2-Max": 1_950 / 3_000_000,
}

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


def run_completion(llm, messages, request):
    """Run the LLM completion with given parameters"""
    prompt_template = ChatPromptTemplate.from_messages(messages)

    chain = prompt_template | llm
    response = chain.invoke({"user_input": request})

    return response


# Create a Flask Blueprint for chat routes
chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/list_models", methods=["GET"])
@run_request
def list_models():
    """List all available models"""
    return jsonify({"models": AVAILABLE_MODELS})


@chat_bp.route("/completion", methods=["POST"])
@run_request
def completion():
    """Send request to LLM and return response"""

    # Get parameters from the request
    data = request.get_json()

    model_id = data.get("model", DEFAULT_MODEL)
    prompt = data.get("prompt", "")
    user_request = data.get("request", "")
    session_id = data.get("session_id")
    user_id = data.get("user_id")
    temperature = data.get("temperature", DEFAULT_TEMPERATURE)
    max_tokens = data.get("max_tokens", DEFAULT_MAX_TOKENS)

    # Validate required parameters
    if not user_request:
        return jsonify({"error": "User request is required"}), 400

    # Handle session logic
    if session_id is None:
        # Create a new session since no session ID was provided
        if not user_id:
            return (
                jsonify({"error": "User ID is required to create a new session"}),
                400,
            )
        session = create_session(user_id, "New Session")
        session_id = session.id
        create_message(session_id, Role.system, prompt)
    else:
        session = get_session_by_id(session_id)
        if not session:
            # Session doesn't exist, but we can create it with a default name
            if not user_id:
                return (
                    jsonify({"error": "User ID is required to create a new session"}),
                    400,
                )

            session = create_session(user_id, "New Session")
            session_id = session.id

    messages = get_messages_by_session_id(session_id)

    conversation_history = []
    for msg in messages:
        conversation_history.append((msg.role.name, msg.content))

    conversation_history.append((Role.human.name, "{user_input}"))
    llm = init_model(model=model_id, temperature=temperature, max_tokens=max_tokens)
    response = run_completion(llm, conversation_history, user_request)

    create_message(session_id, Role.human, user_request)
    create_message(session_id, Role.assistant, response.content)

    usage = response.usage_metadata
    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)

    stats = update_statistics(session_id, input_tokens, output_tokens)
    response_data = {
        "model": model_id,
        "prompt": prompt,
        "response": response.content,
        "session_id": session.id,
        "statistics": {
            "total_input_tokens": stats.total_input_tokens,
            "total_output_tokens": stats.total_output_tokens,
            "last_input_tokens": stats.last_input_tokens,
            "last_output_tokens": stats.last_output_tokens,
        },
        "price": count_price(model_id, stats),
    }

    return jsonify(response_data)


def count_price(model_id, stats: Statistics):
    last_input_price = INPUT_PRICES[model_id] * stats.last_input_tokens
    last_output_price = OUTPUT_PRICES[model_id] * stats.last_output_tokens
    last_request_price = last_input_price + last_output_price

    total_input_price = INPUT_PRICES[model_id] * stats.total_input_tokens
    total_output_price = OUTPUT_PRICES[model_id] * stats.total_output_tokens
    all_requests_price = total_input_price + total_output_price

    return {
        "last_input_price": last_input_price,
        "last_output_price": last_output_price,
        "last_request_price": last_request_price,
        "total_input_price": total_input_price,
        "total_output_price": total_output_price,
        "all_requests_price": all_requests_price,
    }


def convert_role(role):
    role_name = (
        "human"
        if role == Role.human
        else ("assistant" if role == Role.assistent else "system")
    )
    return role_name
