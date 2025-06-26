from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, LoginManager, current_user, logout_user
from .models import User
from .db import db


login_manager = LoginManager()
bp = Blueprint('auth', __name__)

# Add this user_loader function:
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        # Automatically log in user
        login_user(new_user)
        flash("Account created successfully", "success")

        return redirect(url_for('chat.home'))
    
    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

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