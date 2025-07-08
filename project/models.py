"""
Models for user authentication and chat history management.
Classes:
    User (UserMixin, db.Model):
        Represents a user in the system.
        Attributes:
            id (int): Primary key, unique identifier for the user.
            username (str): Unique username for the user, required.
            password_hash (str): Hashed password for authentication, required.
            chats (list of Chat): List of chat records associated with the user.
        Properties:
            password: Write-only property for setting the user's password.
        Methods:
            check_password(password): Verifies a plaintext password against the stored hash.
    Chat (db.Model):
        Represents a chat interaction between a user and the system.
        Attributes:
            id (int): Primary key, unique identifier for the chat record.
            user_id (int): Foreign key referencing the associated user.
            timestamp (datetime): UTC timestamp when the chat was created (defaults to current time).
            prompt (str): The user's input or question.
            response (str): The system's response to the prompt.
"""
from .db import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, timezone

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    chats = db.relationship('Chat', backref='user', lazy=True, cascade='all, delete-orphan')
    
    @property
    def password(self):
        raise AttributeError("Password is write-only")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Chat(db.Model):
    __tablename__ = 'chats'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    prompt = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    