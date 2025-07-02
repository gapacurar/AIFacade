from flask import Flask, render_template, abort
from project.config import Config
from .auth import login_manager
from . import db
from .extensions import limiter
from flask_wtf import CSRFProtect

# Initialize CSRF protection extension
csrf = CSRFProtect()

# Factory function to create and configure the Flask app
def create_app(test_config = None):
    # Create Flask app instance
    app = Flask(__name__)
    # Load default configuration from Config class
    app.config.from_object(Config)

    if test_config is None:
        # Load additional config from file if not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Override config with test settings if provided
        app.config.update(test_config)

    # Initialize Flask extensions with the app
    csrf.init_app(app)           # CSRF protection
    db.init_app(app)             # Database
    login_manager.init_app(app)  # User session/login management
    login_manager.session_protection = "strong"  # Extra session security
    login_manager.login_view = "login"  # Redirect to 'login' view if not authenticated
    limiter.init_app(app)        # Rate limiting

    # Import and register blueprints for modular app structure
    from .chat import bp as chat
    from .auth import bp as auth
    app.register_blueprint(chat)
    app.register_blueprint(auth)

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

    # Set security-related HTTP headers after each request
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

    # Return the configured app instance
    return app
