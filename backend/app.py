from flask import Flask
from flask_cors import CORS
import logging

def create_app():
    app = Flask(__name__)
    CORS(app)
    logging.basicConfig(level=logging.INFO)

    from routes.chat import chat_bp
    from routes.session import session_bp


    app.register_blueprint(chat_bp, url_prefix="/api")
    app.register_blueprint(session_bp, url_prefix="/api")

    return app

app = create_app()
