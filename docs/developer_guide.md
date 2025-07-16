# Developer Guide Document

## Document Control

**TO DO** Please update the Document Control status (date).

- **Version:** 1.0
- **Date:** 2025-06-30
- **Authors:** Bicu Andrei Ovidiu
- **Status:** Final

## Overview

This document will take you through the whole application's infrastructure. This Web Application has been created as a small project.

## 1. QuickStart

For more information about the basic stuff, visit [User Guide](user_guide.md)

## 2. Database

### Models

For the database, we are using SQLite as a local database via Flask_SQLAlchemy. The models we are defining are __User__ and __Chat__.

```python
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
```

For the __user__ model we create a direct relationship with the __chat__  model and we use the @property and @password.setter decorators in order to generate a hash automatically whenever we insert a new User in the database. The check_password function will be used to verify the hash for the login method.

```python
class Chat(db.Model):
    __tablename__ = 'chats'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    prompt = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
```

The __chat__ model is also pretty straightforward. We collect the prompt the user inserted, and we retrieve the response from the api while linking via FK the user_id to the id of the User model. Timestamp is automatically.
I chose this way of storing the responses because it's easier to maintain the history of each individual user and because the session cookies Flask provided are not good enough when it comes to different users logging in from the same device.

### db.py

For the DB, we use the normal SQLAlchemy class from Flask-SQLAlchemy. It's easy to implement and easy to maintain.
In this file, we mostly created the CLI commands for the database with @click.command and @with_appcontext from built-in modules and flask.cli.
The commands we defined are:

1. init-db: We create the initial database and instance/ directory if they don't already exist.
2. delete-tables: We delete all the tables of the database.
3. reset-tables: We delete all the tables, including *alembic_version* if it exists, then we recreate all the tables.

Finally, the init_app() function adds all the commands so they can be called through the app.

Example of CLI command usage:

```sh
flask --app project init-db
```

Output should be:

```sh
Your database has been created.
```

## The Application

Now that we talked about what are our models, which type of persistent database we have and what are our integrated CLI commands, it's time to talk about the architecture of the application.
I used a __factory pattern__ in order to create the application using Flask's __Blueprint__ class to separate core features and to avoid getting any errors due to circular importing. The main app sits in the __init.py__ file inside the project. The blueprints used are: 1. __chat.py__. 2. __auth.py__.

### __init__.py

In this file, we have the factory, which we use in order to create the app. We are using a __config.py__ file in order to import the preset configuration into the application. Before running the application, we also check which config to use, either a __test config__ from __root directory/tests/conftest.py__ or the normal configuration from the __config.py__

```python

    if test_config is None:
        # Load additional config from file if not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Override config with test settings if provided
        app.config.update(test_config)
```

Either way, we initialize our __CSRF protection__ in the app, the __database__, the __login manager__ which handles the user sessions, we set a __session protection__ to *strong* so even if the cookies are stolen any hijack will fail and we also initialize our __limiter__ to limit the requests you can make for a certain amount of time. I also added __CSP protection__ to mitigate XSS and data injection attacks. I implemented CSP via Flask's @after_request decorator.

```python
# Initialize Flask extensions with the app
    csrf.init_app(app)           # CSRF protection
    db.init_app(app)             # Database
    login_manager.init_app(app)  # User session/login management
    login_manager.session_protection = "strong"  # Extra session security
    login_manager.login_view = "login"  # Redirect to 'login' view if not authenticated
    limiter.init_app(app)        # Rate limiting

@app.after_request
    def set_security_headers(response):
        if response is None:
            return response  # Do not modify if response is None

        # Set Content Security Policy to restrict resource loading
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' https://cdn.jsdelivr.net; "
            "style-src 'self' https://cdn.jsdelivr.net; "
            "object-src 'none';"
        )
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Prevent clickjacking by disallowing framing
        response.headers["X-Frame-Options"] = "DENY"
        # Do not send referrer information
        response.headers["Referrer-Policy"] = "no-referrer"
        return response
```

We are using Bootstrap for the styling, that's why we have that at script-src and style-src. We'll go into that later.

Furthermore, the application has two templates for error handling, 404 and 505. Both of these routes are defined directly in the factory app because they have to be **global** and work on any route, not only on a specific blueprint route. For example, if i were to put those routes in **chat** blueprint then only an error from the routes within the chat's routes will redirect correctly.
I also added a **/simulate-505** route in order to test the template, as it is hard to manually simulate the error

```python
    # Custom error handler for 404 Not Found
    @app.errorhandler(404)
    def page_not_found(e):
        # Render custom 404 error page
        return render_template("errors/404.html"), 404 

    # Custom error handler for 505 HTTP Version Not Supported
    @app.errorhandler(505)
    def http_version_not_supported(e):
        # Render custom 505 error page
        return render_template("errors/505.html"), 505

    # Route to simulate a 505 error for testing error handling
    @app.route('/simulate-505')
    def simulate_505():
        abort(505)
```

And in the end, in our __create_app()__ function, where all of this logic lives, we just return the app object

### Blueprints

#### Auth

This blueprint handles all the authentication routes within the application. It handles:

1. /login
2. /register
3. /logout

In here, we also define our LoginManager() class to manage our sessions.

```python
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
```

##### /Register

This route handles the registration and inserts new users into the database. We have 2 methods for this route: POST, GET.

- GET: Renders the registration form.
- POST: Processes registration data, checks for existing users, creates a new user, commits to the database, logs in the new user, and redirects to the chat home page.

We use **Flash** messages to indicate to the user whether the account has been created successfully, if the user already exists in the database, or if something went wrong.
The "something went wrong" indicates that there was an error when trying to add the user to the database. In such a case, to add a new layer of keeping a safe database, we introduced a try block, and if there was an error when trying to commit to the database, we rolled back the session.

```python
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

```

##### /Login

Handles user login via GET and POST requests.
        - GET: Renders the login form.
        - POST: Authenticates the user by username and password, logs in the user if credentials are valid,
          and redirects to the chat home page.
        - If already authenticated, redirects to the chat home page.
        - On failure, it flashes an error message.

Passwords are hashed in the db as stated before, so in order to check the password, we use the User's method *check_password*. This is done via werkzeug_security __check_password_hash__.

```python
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
```

##### /Logout

Logs out the current user, flashes a logout message, and redirects to the login page.

```python
@bp.route("/logout")
def logout():
    logout_user() # This removes the user from the session
    flash("You've been logged out", "info")
    return redirect(url_for("auth.login"))
```

##### Auth Blueprint Dependencies

1. Flask: Blueprint, render_template, request, flash, redirect, url_for
2. Flask-Login: login_user, LoginManager, current_user, logout_user
3. SQLAlchemy model and session management from own modules, db, and models.

##### Notes

The "chat.home" redirect is defined in the chat blueprint.

#### Chat

This blueprint holds the related chat functionality and logic.

1. / - Home page for the chat interface
2. /chat - Handles submission of new chat prompts
3. /clear - Clears the chat history for the current user.

##### /

Redirects to login if the user is not authenticated.
Loads all chat messages for the current user from the database.
Renders the "index.html" template with the user's conversation history

```python
@bp.route("/")
def home():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    
    # Load chats by user id instead of session cookies.
    chats = Chat.query.filter_by(user_id=current_user.id).order_by(Chat.timestamp.asc()).all()
    conversation = [(chat.prompt, chat.response) for chat in chats]
    
    return render_template("index.html", conversation=conversation)
```

Relies on login.html and index.html to be existent.

##### /chat

Validates the prompt lenght and content
Calls the DeepSeek API to generate a response.
Saves the prompt and response to the database, associated with the current user.
Handles errors gracefully, rolling back the database session and flashing error messages as needed.
Redirects back to the home page after processing.

```python
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
```

Relies on index.html template

##### /clear

Deletes all chat records for the current user from the database.
Commits the transaction and flashes a success message.
Redirects back to the home page.

```python
@bp.route("/clear", methods=['POST'])
def clear_chat():
    # Delete all chats for current user
    Chat.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash("Chat history cleared", "success")
    
    return redirect(url_for("chat.home"))
```

Relies on index.html template.

##### Chat Blueprint Dependencies

Flask: For routing, rendering templates, handling requests, and flashing messages.
Flask-Login: For user authentication and access to the current user.
Flask-SQLAlchemy: For database interactions.
Custom modules: models (__Chat__ model), utils (__query_deepseek__), db (__database instance__).

##### Chat Blueprint Notes

All chat data is stored and retrieved per user, ensuring privacy and separation of conversations.
Error handling is implemented for database operations and prompt validation

### schemas.py

In here we hold the schemas which we use to validate the user's input with **pydantic**. We use those schemas to validate input type of constraints, injection via Type Enforcement -- combined with our SQLAlchemy's parameterized queries.

```python
class UserBaseSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=80)
    password: str = Field(..., max_length=128)

    @field_validator("username", "password")
    @classmethod
    def not_empty(cls, value: str, info):
        if not value.strip():
            raise ValueError(f"{info.field_name.capitalize()} cannot be empty")
        return value



class UserRegisterSchema(UserBaseSchema):
    pass


class UserLoginSchema(UserBaseSchema):
    pass

class ChatPromptSchema(BaseModel):
    prompt: str = Field(..., max_length=1000)

    @field_validator("prompt")
    @classmethod
    def not_empty(cls, value: str):
        if not value.strip():
            raise ValueError("Prompt cannot be empty.")
        return value
```

### utils.py

Holds the utility functions for interacting with the LLM's API and rendering responses as markdown.

```python
def query_deepseek(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {current_app.config['DEEPSEEK_API_KEY']}"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            return markdown(result["choices"][0]["message"]["content"])
        else:
            error_msg = response.json().get("error", {}).get("message", "Unknown error")
            return f"API Error {response.status_code}: {error_msg}"
    except Exception as e:
        return f"Error: {str(e)}"
```

Sends a prompt to the DeepSeek chat completion API and returns the response as HTML-rendered Markdown.
    Parameters:
        prompt (str): The user's input or question to be sent to the DeepSeek API.
    Returns:
        str: The API's response is rendered as HTML from Markdown if successful,
             or an error message string if the request fails.
    Raises:
        Exception: Catches and returns any exceptions that occur during the API request.
    Notes:
        - Requires a valid DeepSeek API key set in Flask's current_app configuration under 'DEEPSEEK_API_KEY'.
        - Uses the 'markdown2' library to convert Markdown responses to HTML.
        - Handles API errors gracefully and provides informative error messages.

#### utils.py dependencies

Flask: current_app
Requests: requests
Markdown2: markdown
.env: DEEPSEEK_API_KEY

### config.py

Currently holds only the main Config, but it can be scaled to hold more, such as "Test config" or "Production Config", depending on your needs.
This module loads environment variables using python-dotenv.
Config: Central configuration class for Flask application settings.

```python
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") or "dev-key-123"
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI") # For Flask-Login
    RATELIMIT_DEFAULT = "30 per hour"              # Rate limiting
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RATELIMIT_STORAGE_URI = "memory://"
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
```

Dependencies:
dotenv: load_dotenv
built-in: os

### Extensions

This module initializes and configures the Flask-Limiter extension for rate limiting in a Flask application.
Limiter: An instance of Flask-Limiter configured to use the remote address of the client as the key for rate limiting.
Usage: Import the 'limiter' object and attach it to your Flask app to enable rate limiting based on client IP address.

```python
limiter = Limiter(
    key_func=get_remote_address,
)
```

Dependencies:
Flask-Limiter: Limiter
flask_limiter.util: get_remote_address

### Templates

Are builtin with Flask, Jinja2 and Bootstrap for styling.

Structure:
    base.html - The main layout template. Other templates extend this.
    index.html - Main chat interface shown after login.
    login.html - User login form
    register.html - User registration form
    errors/
        404.html - Renders when a user tries to access a missing page *Not found*.
        505.html - Renders on internal server errors *Server Error*.

Template inheritance:
    - All templates extend **base.html**

```html
{% extends "base.html" %}
```

The **base.html** contains shared *head*, Bootstrap CSS/JS and placeholder blocks like:

```html
{% block title %}{% endblock %}
{% block content %}{% endblock %}
```

#### Template Details

##### index.html

Access: Authenticated users only.
Functionality:
    - Flash messages for notifications.
    - Prompt form to send user input to the assistant.
    - Display chat history *prompt -> response*.
    - Button to clear chat history.
    - Logout button..
Routes assumed:
    Auth blueprint:
        - /logout
    Chat blueprint:
        - /chat
        - /clear

jinja logic:

```jinja2
{% for prompt, response in conversation %}
  <!-- Display prompt and response cards -->
{% endfor %}
```

##### login.html

Access: Public.
Functionality:
    - Login form with username/password
    - Flash messages for login errors or success
    - Link to registration page
Routes:
    Auth blueprint:
        - POST: /login

##### register.html

Access: Public.
Functionality:
    - Form to create a new account.
    - Flash messages for errors *username taken* or success.
    - Link to login page.
Route:
    Auth Blueprint:
        - POST: /register

##### 404.html

Automatically shown when Flask raises a __404 Not Found__ error *Invalid URL*.
Contains a button to redirect the user back to the homepage *__/__*

##### 505.html

Displayed on a 505 error __505 Internal Server Error__.
Contains a button to redirect the user back to the homepage __/__.

#### Security Checks

1. __CSRF__ tokens must be validated.
2. Index should not be accessible without login.
3. Input sanitization for prompt content.

## Testing

In order to ensure everything works accordingly without any errors i've made several test cases in order to test the functionality of the application. We are using a Test config and a temporary database which is created and deleted after each module tested.

Structure:
    conftest.py - holds the Test Configuration and different setups in order to conduct the tests.
    test_auth - Holds all the authentication tests related
    test_chat - Holds all the chat related tests
    test_db_cli - Tests for the CLI commands to ensure they work as intended.
    test_errors - Tests for the 404 and 505 html pages
    test_security - Tests for the __CSP__ and for __session_protection__
    test_app_config - Testing the normal config to see if it works as intended.

### conftest.py

PyTest fixtures for reusable test components.
A helper AuthActions class for simulating user auth.
Temporary database management to isolate test state.

#### Fixtures Overview

Fixture - Scope - Description
app - module - Creates a temporary, fully configured Flask app for tests. Uses a temporary SQLite DB.
client - function - Provides a Flask test client (HTTP-like interface)
runner - function - Provides a CLI runner to test custom CLI commands.
auth - function - Provides methods to register/login/logout test users.
user - function - Creates a blank User model instance for custom setup.

**app** fixture:

```python
@pytest.fixture(scope='module')
def app():
    # Create a temporary file to use as the test database
    db_fd, db_path = tempfile.mkstemp()

    # Create the Flask app with test configuration
    app = create_app({'TESTING': True, 
                      'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}', 
                      'SQLALCHEMY_TRACK_MODIFICATIONS': False,
                      'WTF_CSRF_ENABLED': False,
                      'RATELIMIT_ENABLED': False})

    # Create all database tables
    with app.app_context():
        db.create_all()  

    # Provide the app to the tests
    yield app

    # Cleanup: remove the database and close the file
    with app.app_context():
        db.session.remove()
        for engine in db.engines.values():
            engine.dispose()

    os.close(db_fd)
    os.unlink(db_path)
```

**client** fixture:

```python
@pytest.fixture
def client(app):
    return app.test_client()
```

__runner__ fixture:

```python
@pytest.fixture
def runner(app):
    return app.test_cli_runner()
```

**AuthActions** Class:

```python
class AuthActions(object):
    def __init__(self, client):
        self._client = client
    
    # Register a user (default: username='test', password='test')
    def register(self, username='test', password='test'):
        return self._client.post('/register', data={
                                                'username':username,
                                                'password':password
        })

    # Log in a user (registers first if needed)
    def login(self, username='test', password='test'):
        self.register()
        return self._client.post('/login',
                                 data={'username': username,
                                       'password': password}
    )
    # Log out the current user
    def logout(self):
        return self._client.get('/logout')
```

**auth** and **user** fixtures:

```python
@pytest.fixture
def auth(client):
    return AuthActions(client)

# Fixture to provide a User instance
@pytest.fixture
def user():
    return User()
```

### test_auth

This test suite verifies:
    - User registration
    - Login/Logout flow
    - Authentication state
    - Password hashing & validation
    - Flash messaging & exception handling

#### Test Summary & Behavior

1. register_user - Check if /register route exists and works for a new user
2. user_exists - Ensure duplicate usernames are handled correctly.
3. login - Test successful login and user session state.
4. invalid_login - Handle incorrect login attempts.
5. redirect_logged_in - Redirect logged-in users from login page.
6. logout - Validate logout functionality and session cleanup.
7. password_property_and_check - Ensure passwords are hashed, write-protected and verifiable.
8. register_exception - Simulate a DB commit failure during registration and test user feedback.

### test_chat

This suite verifies:
    - Login enforcement on home/chat
    - Prompt validation *empty, too long*
    - DeepSeek API response handling
    - Flash messages and redirects
    - Chat history cleaning
    - Graceful exception handling

#### Test Summary & Behavior test_chat

1. redirect_home - Ensures unauthenticated users are redirected from __/__ to __/login__
2. prompt_no_message - Prevents empty prompts from being submitted.
3. answer - Simulates DeepSeek API call and checks for mock error response
4. clear_chat - Tests that chat history is cleared and response disappears.
5. prompt_too_long - Validates prompt length enforcement.
6. chat_view_handles_exception - Simulates __query_deepseek()__ failure and ensures app recovers.
7. query_deepseek_exception_handling - Mocks a lower-level failure and checks for error feedback.

### test_db_cli

This suite validates:
    - Custom Flask CLI command behavior
    - Database table creation and deletion
    - Correct output messages.
    - Proper command exit codes

#### Test Summary & Behavior db_cli

1. clear_db_command / init-db / Ensures the database is initialized with all tables created.
2. reset_db_command / reset-tables / Ensures existing tables are dropped and recreated.
3. delete_tables_command / delete-tables / Ensures all tables are dropped from the database.

### test_errors

These tests validate:
    - Custom error page rendering
    - Correct HTTP status codes
    - Friendly error messages shown to users.
    - Presence of helpful UI elements *eg "Go Back Home" button*.

#### Test Summary & Behavior errors

1. error_404_handling - Check if the user is redirected to a user-friendly 404.html
2. error_505_handling - Check if the user is redirected to a user-friendly 505.html

### test_security

This section ensures the application handles advanced security features like session protection and HTTP response headers *CSP*

#### Test Session Protection on User Agent Change

Scenario: Simulate session hijacking via a changed __User-Agent__ header.
Mechanism Tested: Flask-Login's __strong__ session protection.
Expected behavior:
    Session should be invalidated when the __User-Agent__ changes.
    Authenticated user should be logged out automatically.
    Access to protected routes should redirect to login.

Relies on Flask-Login config: __SESSION_PROTECTION = "strong"__

#### Test CSP Headers

Scenario: Check for proper inclusion of Content Security Policty *CSP* headers in response.
Purpose: Helps protect against XSS and data injection attacks.
Expected behavior:
    The header __Content-Security-Policy__ exists.
    It includes a safe policy such as: __"default-src 'self'"__.

### app_config

This test ensures that the Flask application loads configuration variables properly from __config.py__ when no __test_config__ is passed.

Scenario: Validate that the __create_app()__ factory loads settings from __config.py__ when no custom config is supplied.
Checks:
    Configuration values are presend and match expected values
    Verifies **RATELIMIT_DEFAULT**, __DEBUG__ and __WTF_CSRF_ENABLED__ settings are properly applied.

Ensures app doesn't silently boot with missing or incorrect config.

#### Note

We are using __@pytest.mark.last__ to ensure this test is ran last because otherwise it will mess up the test configuration for the other tests.

## Containerization

### Overview Containerization

This application is containerized using Docker and orchestrated via Docker Compose. It runs on production Flask app behind Gunicorn, served through a modern HTTPS-ready reverse proxy with Caddy.

### Dockerfile

Purpose: Build a lightweight Python 3.13 based container with all the dependencies
Features:
    - Based on __python:3.13.5-slim__ for performance and reduced image size.
    - Installs system-level packages for Python modules.
    - Uses __gunicorn__ to serve Flask in production mode.
    - Creates a persistent __instance/__ directory for SQLite DB.

```dockerfile
CMD ["gunicorn", "--config", "gunicorn.conf.py", "project:create_app()"]
```

### docker-compose.yml

Purpose: Orchestrates services for:
    - Flask app, *Gunicorn*.
    - Reverse proxy *Caddy*.
    - Volume mounting for dev DB and Caddy self-signed certs.

### gunicorn.conf

Purpose: Production WSGI server configuration

```python
bind = "0.0.0.0:5000"
workers = 4
timeout = 120
keepalive = 5
accesslog = "-"
errorlog = "-"
```

1. workers = 4 - Handles concurrenct requests (adjust for CPU count)
2. timeout = 120 - Allows long-running inference/chat requests.
3. accesslog = "-" - Logs to stdout for container visibility

### Caddyfile

Purpose: Automatically handles TLS & proxies traffic for flask

```Caddyfile
localhost {
    reverse_proxy web:5000
    tls internal
}
```

localhost - Serve app locally on HTTPS
revers_proxy web:5000 - Proxies traffic to Flask container
tls_internal - Uses internal CA (use Let's Encrypt in prod).

## CI/CD Pipeline via GitHub Actions

### Overview CI/CD

This project includes a GitHub Actions workflow that automates the process of:

1. Checking out your code.
2. Building Docker containers.
3. Spinning up the services.
4. Running unit/integration tests.
5. Tearing everything down cleanly.

### Trigger

This workflow is automatically triggered on __push__ events on:
    - main
    - final-exam

### Job Breakdown

1. Checkout code - Clones your repo into the runner
2. Set up Docker - Initializes Docker Buildx support
3. Build containers - Uses __docker-compose.yml__ to build all services
4. Run containers - Launches services in detached mode
5. Wait for app - Optional buffer to let Flask/Gunicorn fully start.
6. Run tests - Executes all tests in the __tests/__ folder using __pytest__.
7. Tear down - Cleans up containers associated volumes.

## Final Notes

Developers are encouraged to follow the comments in the source code closely. These often contain important configuration instructions or warnings that affect correct deployment and use.

For feedback, issues, or contributions, please contact the author: [https://github.com/oveandrei](https://github.com/oveandrei).
