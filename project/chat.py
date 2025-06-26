# DeepSeek Chatbot Application
# This application uses Flask, Flask-Login, and aiohttp to create a chatbot interface
# that interacts with the DeepSeek API. It includes user authentication, rate limiting,
# and a simple chat interface. The responses from DeepSeek are rendered in Markdown format.

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from .models import Chat  # Import after db is defined in models.py
from .extensions import limiter
from .utils import query_deepseek
from .db import db


bp = Blueprint('chat', __name__)


# Routes
@bp.route("/")
@limiter.limit("10 per minute")
def home():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    
    # Load chats by user id instead of session cookies.
    chats = Chat.query.filter_by(user_id=current_user.id).order_by(Chat.timestamp.asc()).all()
    conversation = [(chat.prompt, chat.response) for chat in chats]
    
    return render_template("index.html", conversation=conversation)


@bp.route("/chat", methods=["POST"])
@limiter.limit("5 per minute")
def chat():
    prompt = request.form["prompt"]
    
    if not prompt.strip():
        flash("Please enter a message", "error")
        return redirect(url_for("chat.home"))

    # Get response from DeepSeek
    answer = query_deepseek(prompt)

    # Save to database
    new_chat = Chat(
        user_id = current_user.id,
        prompt=prompt,
        response = answer,
    )
    db.session.add(new_chat)
    db.session.commit()

    return redirect(url_for("chat.home"))


@bp.route("/clear", methods=['POST'])
def clear_chat():
    # Delete all chats for current user
    Chat.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash("Chat history cleared", "success")
    
    return redirect(url_for("chat.home"))




