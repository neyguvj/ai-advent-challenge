from flask import Flask
from app.routes.users import users_bp
from app.routes.chat import chat_bp
from app.routes.sessions import sessions_bp
from app.routes.messages import messages_bp
from app.routes.health import health_bp
from app.db.setup import setup as db_setup


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)

    # Register the blueprints
    app.register_blueprint(users_bp, url_prefix="/api")
    app.register_blueprint(chat_bp, url_prefix="/api")
    app.register_blueprint(sessions_bp, url_prefix="/api")
    app.register_blueprint(messages_bp, url_prefix="/api")
    app.register_blueprint(health_bp, url_prefix="/api")
    app.debug = True
    return app


db_setup()
app = create_app()
