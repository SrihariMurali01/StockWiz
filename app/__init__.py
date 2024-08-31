from flask import Flask
import os
from dotenv import load_dotenv

def create_app():
    # Load environment variables from .env file
    load_dotenv()

    # Initialize the Flask application
    app = Flask(__name__)

    # Register blueprints (we'll add the routes later)
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
