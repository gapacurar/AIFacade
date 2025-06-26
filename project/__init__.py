from flask import Flask
from project.config import Config
from .auth import login_manager
from . import db
from .extensions import limiter
from flask.cli import with_appcontext
from flask_migrate import upgrade
import click

# Initialize APP & Extensions
def create_app(test_config = None):
    app = Flask(__name__)
    app.config.from_object(Config)


    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"
    limiter.init_app(app)

    
    from .chat import bp as chat
    from .auth import bp as auth
    from .errors import bp as errors
    app.register_blueprint(chat)
    app.register_blueprint(auth)
    app.register_blueprint(errors)
    
    return app


