from flask import Flask
from config import config


def create_app(config_name="development"):
    """
    Flask application factory function.

    Args:
    config_name (str): Configuration name ('development', 'production', 'testing').

    Returns:
    Flask: A configured Flask application instance.
    """

    # create the Flask application instance
    app = Flask(__name__)

    # Load the configuration based on the config.py
    app.config.from_object(config[config_name])

    # register routes (URL)
    from app.routes import main

    app.register_blueprint(main.bp)
    return app
