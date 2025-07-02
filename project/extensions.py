
"""
This module initializes and configures the Flask-Limiter extension for rate limiting in a Flask application.
Attributes:
    limiter (Limiter): An instance of Flask-Limiter configured to use the remote address of the client as the key for rate limiting.
Usage:
    Import the `limiter` object and attach it to your Flask app to enable rate limiting based on client IP address.
Example:
    app = Flask(__name__)
    limiter.init_app(app)
"""
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter


limiter = Limiter(
    key_func=get_remote_address,
)