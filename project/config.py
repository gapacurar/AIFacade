
"""
Configuration module for the application.
This module loads environment variables using python-dotenv and defines the Config class,
which contains all configuration settings for the application.
Classes:
    Config: Central configuration class for Flask application settings.
Config class attributes:
    SECRET_KEY (str): Secret key for session management and CSRF protection.
    DEEPSEEK_API_KEY (str): API key for DeepSeek integration, loaded from environment.
    SQLALCHEMY_DATABASE_URI (str): Database URI for SQLAlchemy and Flask-Login.
    RATELIMIT_DEFAULT (str): Default rate limit policy (e.g., "30 per hour").
    SQLALCHEMY_TRACK_MODIFICATIONS (bool): Flag to disable SQLAlchemy modification tracking.
    RATELIMIT_STORAGE_URI (str): URI for rate limit storage backend (default: in-memory).
    WTF_CSRF_ENABLED (bool): Enables CSRF protection for Flask-WTF forms.
    WTF_CSRF_TIME_LIMIT (int or None): Time limit for CSRF tokens (None disables expiration).
"""
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") or "dev-key-123"
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI") # For Flask-Login
    RATELIMIT_DEFAULT = "30 per hour"              # Rate limiting
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RATELIMIT_STORAGE_URI = "memory://"
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
