from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

db = SQLAlchemy()

def create_app():
    load_dotenv()


    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-key")

    DB_USER = "root"
    DB_PASS = "rootadmin123"
    DB_HOST = "127.0.0.1"
    DB_NAME = "chatbot"

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}?charset=utf8mb4"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app
