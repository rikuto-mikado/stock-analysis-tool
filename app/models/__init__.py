from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Create SQLAlchemy instance
db = SQLAlchemy()


def init_db(app):
    """
    Function to initialize the database

    Args:
        app (_type_): _description_
    """
    # Initialize hte SQLAlchemy with the flask
    db.init_app(app)

    # create tables within the application context
    with app.app_context():
        # Import all models (for table creation)
        from app.models.stock import Stock
        from app.models.price_history import PriceHistory
        from app.models.watchlist import Watchlist

        # Create tables
        db.create_all()
        print("Database tables created successfully!")


# Base model class used across models
class BaseModel(db.Model):
    """
    Base class for all models
    Provides common columns and utility methods
    """

    __abstract__ = True

    # common columns
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def save(self):
        """Save to the database"""
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error saving to database: {e}")
            return False

    def delete(self):
        """Delete from the database"""
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting from database: {e}")
            return False

    def to_dict(self):
        """Convert to a dictionary (for JSON serialization)"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            # Convert datetime objects to strings
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result

    def __repr__(self):
        """String representation for debugging"""
        return f"<{self.__class__.__name__} {self.id}>"
