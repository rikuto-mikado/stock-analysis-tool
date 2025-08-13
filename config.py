import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Base configuration
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL") or "sqlite:///stock_analysis.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Stock API settings
    ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")
    FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY")

    # Application settings
    TIMEZONE = os.environ.get("TIMEZONE") or "Asia/Tokyo"
    DEFAULT_CURRENCY = os.environ.get("DEFAULT_CURRENCY") or "JPY"


class DevelopmentConfig(Config):  # 修正: 継承を正しく
    # Development configuration
    DEBUG = True
    SQLALCHEMY_ECHO = True  # SQLクエリをログ出力


class ProductionConfig(Config):
    # Production configuration
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    # Testing configuration
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


# Setting of dictionary
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
