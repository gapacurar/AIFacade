
"""
chat.py
This module defines the chat blueprint for the Flask application, handling chat-related routes and logic.
Blueprints:
    bp: Flask Blueprint instance for chat-related routes.
Routes:
    - "/" (GET): Home page for the chat interface.
        * Redirects to login if the user is not authenticated.
        * Loads all chat messages for the current user from the database, ordered by timestamp.
        * Renders the "index.html" template with the user's conversation history.
    - "/chat" (POST): Handles submission of new chat prompts.
        * Validates the prompt length and content.
        * Calls the DeepSeek API to generate a response.
        * Saves the prompt and response to the database, associated with the current user.
        * Handles errors gracefully, rolling back the database session and flashing error messages as needed.
        * Redirects back to the home page after processing.
    - "/clear" (POST): Clears the chat history for the current user.
        * Deletes all chat records for the current user from the database.
        * Commits the transaction and flashes a success message.
        * Redirects back to the home page.
Dependencies:
    - Flask: For routing, rendering templates, handling requests, and flashing messages.
    - Flask-Login: For user authentication and access to the current user.
    - SQLAlchemy: For database interactions.
    - Custom modules: models (Chat model), extensions (limiter), utils (query_deepseek), db (database instance).
Notes:
    - All chat data is stored and retrieved per user, ensuring privacy and separation of conversations.
    - Error handling is implemented for database operations and prompt validation.
    - The DeepSeek API is used to generate responses to user prompts.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from .models import Chat  # Import after db is defined in models.py
from .utils import query_deepseek
from .db import db


bp = Blueprint('chat', __name__)


# Routes
@bp.route("/")
def home():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    
    # Load chats by user id instead of session cookies.
    chats = Chat.query.filter_by(user_id=current_user.id).order_by(Chat.timestamp.asc()).all()
    conversation = [(chat.prompt, chat.response) for chat in chats]
    
    return render_template("index.html", conversation=conversation)


@bp.route("/chat", methods=["POST"])
def chat():
    prompt = request.form["prompt"]

    if len(prompt) > 1000:
        flash("Prompt too long.", "error")
        return redirect(url_for("chat.home"))
    
    if not prompt.strip():
        flash("Please enter a message", "error")
        return redirect(url_for("chat.home"))

    try:
        # Get response from DeepSeek
        answer = query_deepseek(prompt) # Custom function to query DeepSeek API from utils.py

        # Save to database
    
        new_chat = Chat(
            user_id = current_user.id,
            prompt=prompt,
            response = answer,
        )
        db.session.add(new_chat)
        db.session.commit()
    
    except Exception as e:
        db.session.rollback()
        flash("Something went wrong.", "error")

    return redirect(url_for("chat.home"))


@bp.route("/clear", methods=['POST'])
def clear_chat():
    # Delete all chats for current user
    Chat.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash("Chat history cleared", "success")
    
    return redirect(url_for("chat.home"))




