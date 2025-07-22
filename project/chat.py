"""
chat.py
This module defines the chat blueprint for handling chat-related routes in the Flask application.
Blueprints:
    bp: Flask Blueprint for chat routes.
Routes:
    - "/" (GET): Home page displaying the user's chat history.
        * Redirects to login if the user is not authenticated.
        * Retrieves all chat messages for the current user, ordered by timestamp.
        * Renders 'index.html' with the conversation history.
    - "/chat" (POST): Handles chat prompt submissions.
        * Validates the submitted prompt using ChatPromptSchema.
        * If validation fails, flashes error messages and redirects to home.
        * Queries DeepSeek for a response to the prompt.
        * Saves the prompt and response as a new Chat entry in the database.
        * Handles database errors by rolling back and flashing an error message.
        * Redirects to home after processing.
    - "/clear" (POST): Clears the user's chat history.
        * Deletes all chat entries for the current user.
        * Commits the transaction and flashes a success message.
        * Handles errors by rolling back and flashing an error message.
        * Redirects to home after processing.
Dependencies:
    - Flask (Blueprint, render_template, request, redirect, url_for, flash)
    - flask_login (current_user)
    - .models (Chat)
    - .utils (query_deepseek)
    - .db (db)
    - pydantic (ValidationError)
    - .schemas (ChatPromptSchema)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
# Blueprint: For modular route organization
# render_template: To render HTML templates
# request: To access form data from POST requests
# redirect, url_for: For redirecting users and generating URLs
# flash: For displaying feedback messages to users

from flask_login import current_user
# current_user: To check authentication and get the current user's ID

from .models import Chat  # Import after db is defined in models.py
# Chat: The database model for storing chat messages

from .utils import query_deepseek
# query_deepseek: Utility function to get responses from the DeepSeek API

from .db import db
# db: SQLAlchemy database instance for database operations

from pydantic import ValidationError
# ValidationError: To handle validation errors from Pydantic schemas

from .schemas import ChatPromptSchema
# ChatPromptSchema: Pydantic schema for validating chat prompts


bp = Blueprint('chat', __name__)


# Routes
@bp.route("/")
def home():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))

    chats = Chat.query.filter_by(user_id=current_user.id).order_by(Chat.timestamp.asc()).all()
    conversation = [(chat.prompt, chat.response) for chat in chats]
    return render_template("index.html", conversation=conversation)


@bp.route("/chat", methods=["POST"])
def chat():
    try:
        data = ChatPromptSchema(**request.form)
    except ValidationError as e:
        for err in e.errors():
            flash(err["msg"], "error")
        return redirect(url_for("chat.home"))

    try:
        # Get response from DeepSeek
        answer = query_deepseek(data.prompt)

        # Save chat
        new_chat = Chat(
            user_id=current_user.id,
            prompt=data.prompt,
            response=answer,
        )
        db.session.add(new_chat)
        db.session.commit()

    except Exception:
        db.session.rollback()
        flash("Something went wrong while saving the chat.", "error")

    return redirect(url_for("chat.home"))


@bp.route("/clear", methods=["POST"])
def clear_chat():
    try:
        Chat.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        flash("Chat history cleared", "success")
    except Exception:
        db.session.rollback()
        flash("Could not clear chat history", "error")

    return redirect(url_for("chat.home"))




