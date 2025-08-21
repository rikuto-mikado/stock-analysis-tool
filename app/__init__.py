from flask import Flask
from config import config


def create_app(config_name="development"):
    """
    Flask application factory function

    Args:
    config_name (str): Configuration name ('development', 'production', 'testing')

    Returns:
    Flask: Configured Flask application
    """

    # create the Flask application instance
    app = Flask(__name__)

    # Load the configuration based on the config.py
    app.config.from_object(config[config_name])

    # Initialize database
    initialize_database(app)

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    return app


def initialize_database(app):
    """
    Initialize database with the Flask app

    Args:
    app: Flask application instance
    """
    from app.models import db

    # Initialize SQLAlchemy with the app
    db.init_app(app)

    # Create tables if they don't exist (in development)
    if app.config.get("ENV") == "development":
        with app.app_context():
            # Import all models to ensure tables are created
            from app.models.stock import Stock
            from app.models.price_history import PriceHistory
            from app.models.watchlist import Watchlist

            # Create all tables
            db.create_all()
            print("Database tables created/verified")


def register_blueprints(app):
    """
    Register all blueprints with the Flask app

    Args:
    app: Flask application instance
    """

    # Main routes (home, about)
    from app.routes import main

    app.register_blueprint(main.bp)


def register_error_handlers(app):
    """
    Register error handlers for the Flask app

    Args:
    app: Flask application instance
    """

    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template

        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        from app.models import db

        db.session.rollback()
        return render_template("errors/500.html"), 500
