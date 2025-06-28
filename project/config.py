import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") or "dev-key-123"
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///users.db")  # For Flask-Login
    RATELIMIT_DEFAULT = "5 per minute"              # Rate limiting
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RATELIMIT_STORAGE_URI = "memory://"
