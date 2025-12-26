from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import logging
load_dotenv()
def create_app():
    app = Flask(__name__)
    CORS(app)
    # basic logging
    logging.basicConfig(level=logging.INFO)
    # register routes
    from routes.chat import chat_bp
    from routes.session import session_bp   
    app.register_blueprint(chat_bp)
    app.register_blueprint(session_bp)     
    return app
app = create_app()


