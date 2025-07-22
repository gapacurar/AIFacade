"""
- Flask (from flask import Blueprint, render_template, request, flash, redirect, url_for)
    # Used for creating blueprints, rendering templates, handling requests, flashing messages, and redirects.
- Flask-Login (from flask_login import login_user, LoginManager, current_user, logout_user)
    # Provides user session management for Flask, including login, logout, and user loading.
- Pydantic (from pydantic import ValidationError)
    # Used for validating and parsing user input data via schemas.
- SQLAlchemy (from .db import db)
    # Database ORM for managing user data and sessions.
- Custom User model and schemas (from .models import User, from .schemas import UserRegisterSchema, UserLoginSchema)
    # User model for database operations and Pydantic schemas for input validation.
auth.py
This module defines authentication routes and logic for user registration, login, and logout
using Flask, Flask-Login, and Pydantic for input validation.
Blueprints:
    bp (Blueprint): The authentication blueprint for registering auth-related routes.
Functions:
    load_user(user_id):
        Flask-Login user loader callback. Loads a user from the database by user ID.
    register():
        Handles user registration.
        - GET: Renders the registration form.
        - POST: Validates input using Pydantic, checks for existing user, creates a new user,
          logs them in, and redirects to the chat home page. Handles validation and database errors.
    login():
        Handles user login.
        - GET: Renders the login form.
        - POST: Validates input using Pydantic, checks credentials, logs in the user, and redirects
          to the chat home page. Handles validation errors and incorrect credentials.
    logout():
        Logs out the current user and redirects to the login page.
Dependencies:
    - Flask
    - Flask-Login
    - Pydantic
    - SQLAlchemy (for database session)
    - Custom User model and schemas
Templates:
    - register.html: Registration form template.
    - login.html: Login form template.
Flash Messages:
    - Used for displaying success, error, and info messages to the user.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, LoginManager, current_user, logout_user
from .models import User
from .db import db
from pydantic import ValidationError
from .schemas import UserRegisterSchema, UserLoginSchema


login_manager = LoginManager()
bp = Blueprint('auth', __name__)

# Load user by ID for session management
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@bp.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            data = UserRegisterSchema(**request.form)
        
        except ValidationError as e:
            for err in e.errors():
                flash(err["msg"], "error")
            return redirect(url_for("auth.register"))

        # Check if user already exists
        if User.find_by_username(data.username):
            flash("User already exists.", "error")
        
        # Create new user
        try:
            new_user = User()
            new_user.username = data.username
            new_user.password = data.password

            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)
            flash("Account created successfully", "success")
            return redirect(url_for("chat.home"))
        
        except Exception as e:
            db.session.rollback()
            flash("Something went wrong during registration.", "error")
            return redirect(url_for("auth.register"))
    
    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("chat.home"))

    if request.method == "POST":
        try:
            # Validate input using Pydantic
            data = UserLoginSchema(**request.form)
        except ValidationError as e:
            for err in e.errors():
                flash(err["msg"], "error")
            return redirect(url_for("auth.login"))

        # Check user credentials
        user = User.find_by_username(data.username)
        if user and user.check_password(data.password):
            login_user(user)
            flash("Logged in successfully", "success")
            return redirect(url_for("chat.home"))
        else:
            flash("Invalid username or password", "error")

    return render_template("login.html")

@bp.route("/logout")
def logout():
    logout_user()
    flash("You've been logged out", "info")
    return redirect(url_for("auth.login"))