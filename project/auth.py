from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, LoginManager, current_user, logout_user
from .models import User
from .db import db

"""
auth.py
This module defines authentication routes and logic for a Flask web application using Flask-Login.
It provides user registration, login, and logout functionality, and integrates with a SQLAlchemy database.
Blueprints:
    bp (Blueprint): The authentication blueprint registered as 'auth'.
Functions:
    load_user(user_id):
        Flask-Login user loader callback.
        Retrieves a User object from the database by user_id for session management.
    register():
        Handles user registration via GET and POST requests.
        - GET: Renders the registration form.
        - POST: Processes registration data, checks for existing users, creates a new user,
          commits to the database, logs in the new user, and redirects to the chat home page.
        - On error, flashes an error message and redirects appropriately.
    login():
        Handles user login via GET and POST requests.
        - GET: Renders the login form.
        - POST: Authenticates the user by username and password, logs in the user if credentials are valid,
          and redirects to the chat home page.
        - If already authenticated, redirects to the chat home page.
        - On failure, flashes an error message.
    logout():
        Logs out the current user, flashes a logout message, and redirects to the login page.
Dependencies:
    - Flask (Blueprint, render_template, request, flash, redirect, url_for)
    - Flask-Login (login_user, LoginManager, current_user, logout_user)
    - SQLAlchemy models and session management (User, db)
Notes:
    - Passwords should be securely hashed and checked using appropriate methods in the User model.
    - Flash messages are used to provide feedback to the user.
    - The 'chat.home' endpoint is assumed to be defined elsewhere in the application.
"""


login_manager = LoginManager()
bp = Blueprint('auth', __name__)

# Add this user_loader function:
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@bp.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get username and password
        username = request.form.get("username")
        password = request.form.get("password")
        # Check if already exists
        user = User.query.filter_by(username=username).first()

        if user:
            flash("User already exists.", "error")
            return redirect(url_for("auth.register"))
        
        # Register user
        try:
            new_user = User(username=username)
            new_user.password = password
            db.session.add(new_user)
            db.session.commit()
        
            # Automatically log in user
            login_user(new_user)
            flash("Account created successfully", "success")
            
        except Exception as e:
            db.session.rollback()
            flash("Something went wrong.", "error")

        return redirect(url_for('chat.home'))
    
    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("chat.home"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("chat.home"))
        else:
            flash("Invalid username or password", "error")

    return render_template("login.html")

@bp.route("/logout")
def logout():
    logout_user()
    flash("You've been logged out", "info")
    return redirect(url_for("auth.login"))