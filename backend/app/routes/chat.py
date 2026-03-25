from flask import Blueprint, request, jsonify
import os
from langchain_gigachat.chat_models import GigaChat
from langchain_core.prompts import ChatPromptTemplate
from app.routes.utils import run_request
from app.db.sessions import create_session, get_session_by_id
from app.db.messages import create_message, get_messages_by_session_id
from app.db.models import Role

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
    create_message(session_id, Role.assistent, response.content)

    return jsonify(
        {
            "model": model_id,
            "prompt": prompt,
            "response": response.content,
            "session_id": session.id,
        }
    )


def convert_role(role):
    role_name = (
        "human"
        if role == Role.human
        else ("assistant" if role == Role.assistent else "system")
    )
    return role_name
