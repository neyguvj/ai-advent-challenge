import sys

from flask import Blueprint, request, jsonify
import os

from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware

from langchain_gigachat.chat_models import GigaChat
from langchain_core.prompts import ChatPromptTemplate


from app.routes.utils import run_request
from app.db import get_connection
from app.db.models import Statistics
from app.db.sessions import create_session, get_session_by_id
from app.db.statistics import update_statistics
from app.db.checkpointer import get_checkpointer
from app.db.messages import get_history_by_session_id
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory


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

    checkpointer = get_checkpointer(get_connection())

    agent = create_agent(
        llm,
        middleware=[
            SummarizationMiddleware(
                model=llm,
                trigger=("tokens", 200),
                keep=("messages", 2),
            ),
        ],
        checkpointer=checkpointer,
    )

    return agent


def run_completion(llm, prompt, request, session_id):
    """Run the LLM completion with given parameters"""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{user_input}"),
        ]
    )

    chain = prompt | llm
    chain_with_history = RunnableWithMessageHistory(
        chain,
        get_history_by_session_id,
        input_messages_key="user_input",
        history_messages_key="history",
    )
    response = chain_with_history.invoke(
        {"user_input": request},
        config={"configurable": {"session_id": session_id, "thread_id": session_id}},
    )

    return response["messages"][-1]


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

    llm = init_model(model=model_id, temperature=temperature, max_tokens=max_tokens)
    session_id = get_session(user_id, session_id, user_request)
    response = run_completion(llm, prompt, user_request, session_id)

    usage = response.usage_metadata
    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)

    stats = update_statistics(session_id, input_tokens, output_tokens)
    response_data = {
        "model": model_id,
        "prompt": prompt,
        "response": response.content,
        "session_id": session_id,
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


def get_session(user_id, session_id, user_request) -> str:
    if session_id is None:
        # Create a new session since no session ID was provided
        if not user_id:
            raise ValueError("User ID is required to create a new session")
        session = create_session(user_id, user_request)
        return str(session.id)
    else:
        session = get_session_by_id(session_id)
        if not session:
            if not user_id:
                raise ValueError("User ID is required to create a new session")
            session = create_session(user_id, user_request)
            return str(session.id)
    return session_id
