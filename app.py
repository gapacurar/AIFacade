# DeepSeek Chatbot Application
# This application uses Flask, Flask-Login, and aiohttp to create a chatbot interface
# that interacts with the DeepSeek API. It includes user authentication, rate limiting,
# and a simple chat interface. The responses from DeepSeek are rendered in Markdown format.
    
import asyncio
import aiohttp
from flask import Flask, render_template, request, session, redirect, url_for
from flask_login import LoginManager, login_user, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from markdown2 import markdown
#from models import User, db
from config import Config
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, current_user, logout_user
from models import User
from werkzeug.security import check_password_hash
from models import db, User  # Import after db is defined in models.py
# Initialize Flask
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = "login"

# Add this user_loader function:
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Rate Limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[app.config["RATELIMIT_DEFAULT"]]
)
limiter.init_app(app)


# Async DeepSeek Query
async def query_deepseek(prompt):
    headers = {"Authorization": f"Bearer {app.config['DEEPSEEK_API_KEY']}"}
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        async with aiohttp.ClientSession() as client:
            async with client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return markdown(result["choices"][0]["message"]["content"])
                return "API Error: Rate limit exceeded"
    except Exception as e:
        return f"Error: {str(e)}"

# Routes
# @app.route("/")
@app.route("/")
@limiter.limit("10 per minute")
def home():
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    return render_template("index.html", conversation=session.get("conversation", []))

@limiter.limit("10 per minute")
def home():
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    return render_template("index.html", conversation=session.get("conversation", []))

@app.route("/chat", methods=["POST"])
@limiter.limit("5 per minute")
async def chat():
    prompt = request.form["prompt"]
    answer = await query_deepseek(prompt)
    session.setdefault("conversation", []).append((prompt, answer))
    return redirect(url_for("home"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password", "error")

    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))

# Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5001, debug=True)

