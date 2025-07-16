"""
models.py
This module defines the SQLAlchemy ORM models for the application's database, including the User and Chat models.
Classes:
    User (UserMixin, db.Model):
        Represents a user in the system.
        - id: Primary key (int).
        - username: Unique username (str).
        - password: Write-only property for setting the user's password (hashed).
        - chats: Relationship to Chat objects associated with the user.
        Methods:
            - check_password(password): Verifies a password against the stored hash.
            - find_by_username(username): Class method to find a user by username.
    Chat (db.Model):
        Represents a chat record associated with a user.
        - id: Primary key (int).
        - user_id: Foreign key referencing User.id (int).
        - timestamp: Date and time of the chat (datetime, UTC).
        - prompt: The user's prompt (str).
        - response: The system's response (str).
        Properties:
            - user_id: Hybrid property for querying and instance access.
            - timestamp: Hybrid property for querying and instance access.
            - prompt: The prompt text.
            - response: The response text.
Notes:
    - Passwords are stored as hashes using Werkzeug security utilities.
    - The User model uses private attributes with public properties for encapsulation.
    - The Chat model uses hybrid properties for user_id and timestamp to support both instance access and query expressions.
    - Relationships are set up with cascading deletes for user chats.
"""
from .db import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, timezone
from sqlalchemy.ext.hybrid import hybrid_property

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    __id = db.Column("id", db.Integer, primary_key=True)
    __username = db.Column("username", db.String(80), unique=True, nullable=False)
    __password_hash = db.Column("password", db.String(128), nullable=False)
    __chats = db.relationship('Chat', backref='user', lazy=True, cascade='all, delete-orphan')
    
    @property
    def id(self):
        return self.__id

    @property
    def username(self):
        return self.__username

    @username.setter
    def username(self, username):
        if not username:
            raise ValueError("Username cannot be empty")
        self.__username = username

    @property
    def password(self):
        raise AttributeError("Password is write-only")

    @password.setter
    def password(self, password):
        if not password:
            raise ValueError("Password cannot be empty")
        self.__password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.__password_hash, password)

    @property
    def chats(self):
        return self.__chats

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter(cls._User__username == username).first()



class Chat(db.Model):
    __tablename__ = 'chats'

    __id = db.Column("id", db.Integer, primary_key=True)
    __user_id = db.Column("user_id", db.Integer, db.ForeignKey('user.id'), nullable=False)
    __timestamp = db.Column("timestamp", db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    __prompt = db.Column("prompt", db.Text, nullable=False)
    __response = db.Column("response", db.Text, nullable=False)

    @property
    def id(self):
        return self.__id

    @hybrid_property
    def user_id(self):
        return self.__user_id

    @user_id.expression
    def user_id(cls):
        return cls.__table__.c.user_id   

    @user_id.setter
    def user_id(self, value):
        if not isinstance(value, int):
            raise ValueError("user_id must be an integer")
        self.__user_id = value

    @hybrid_property
    def timestamp(self):
        # Return actual datetime value on instance
        return self.__timestamp

    @timestamp.expression
    def timestamp(cls):
        # Return column for query usage
        return cls.__table__.c.timestamp

    @property
    def prompt(self):
        return self.__prompt

    @prompt.setter
    def prompt(self, val):
        if not val:
            raise ValueError("Prompt cannot be empty")
        self.__prompt = val

    @property
    def response(self):
        return self.__response

    @response.setter
    def response(self, val):
        if not val:
            raise ValueError("Response cannot be empty")
        self.__response = val