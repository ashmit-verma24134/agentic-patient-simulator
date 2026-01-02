from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import logging

load_dotenv()
def create_app():
    app = Flask(__name__)   #flask app factor pattern for clean architecture
    CORS(
        app,resources={r"/api/*":{"origins":"http://localhost:5500"}}
    )
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    from routes.chat import chat_bp              #routing of session and chat
    from routes.session import session_bp
    app.register_blueprint(session_bp)
    app.register_blueprint(chat_bp)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
