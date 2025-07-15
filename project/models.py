"""
models.py
This module defines the database models for the application, including the User and Chat models.
It uses SQLAlchemy for ORM mapping and integrates with Flask-Login for user session management.
Classes:
    User (UserMixin, db.Model):
        Represents a user in the system.
        Attributes:
            id (int): Primary key.
            __username (str): Unique username for the user.
            __password_hash (str): Hashed password.
            chats (list[Chat]): List of associated Chat objects.
        Properties:
            username (str): Getter and setter for the username.
            password (write-only): Setter for the password, hashes the password.
        Methods:
            check_password(password): Checks if the provided password matches the stored hash.
            find_by_username(username): Class method to find a user by username.
    Chat (db.Model):
        Represents a chat message between a user and the system.
        Attributes:
            id (int): Primary key.
            user_id (int): Foreign key referencing User.
            timestamp (datetime): Time when the chat was created (UTC).
            __prompt (str): The user's prompt.
            __response (str): The system's response.
        Properties:
            prompt (str): Getter and setter for the prompt.
            response (str): Getter and setter for the response.
"""

from .db import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, timezone

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    __username = db.Column("username", db.String(80), unique=True, nullable=False)
    __password_hash = db.Column("password", db.String(128), nullable=False)
    chats = db.relationship('Chat', backref='user', lazy=True, cascade='all, delete-orphan')
    
    # setter getter username
    @property
    def username(self):
        return self.__username
    
    @username.setter
    def username(self, username):
        if not username:
            raise ValueError("Username cannot be empty")
        self.__username = username


    # setter getter password
    @property
    def password(self):
        raise AttributeError("Password is write-only")

    @password.setter
    def password(self, password):
        self.__password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.__password_hash, password)

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter(cls._User__username == username).first()
    
class Chat(db.Model):
    __tablename__ = 'chats'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    __prompt = db.Column("prompt", db.Text, nullable=False)
    __response = db.Column("response", db.Text, nullable=False)
    
    @property
    def prompt(self):
        return self.__prompt
    
    @prompt.setter
    def prompt(self, val):
        self.__prompt = val

    @property
    def response(self):
        return self.__response
    
    @response.setter
    def response(self, val):
        self.__response = val