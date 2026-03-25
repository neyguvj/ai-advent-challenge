from flask import jsonify
import logging
from functools import wraps

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_request(func):
    """
    A utility function that handles exceptions and transforms responses to JSON.

    Args:
        func: The function to be wrapped

    Returns:
        A wrapper function that handles exceptions and returns JSON responses
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            # If the function returns a JSON-serializable object, return it directly
            if isinstance(result, (dict, list)):
                return jsonify(result)
            # If the function returns a Flask response object, return it as-is
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            return jsonify({"error": str(e)}), 500

    return wrapper
