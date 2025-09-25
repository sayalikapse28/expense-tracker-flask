import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-in-production")

    # Get DB URL from env or fallback to SQLite
    uri = os.environ.get("DATABASE_URL", "sqlite:///expenses.db")

    # Render gives postgres:// but SQLAlchemy needs postgresql://
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
