from flask import Flask, render_template, abort
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


    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.update(test_config)
        app.config["RATELIMIT_DEFAULT"] = "20 per minute"

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"
    limiter.init_app(app)
    
    from .chat import bp as chat
    from .auth import bp as auth
    app.register_blueprint(chat)
    app.register_blueprint(auth)



    # Handle 404 errors
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404 
    # Handle 505 errors
    @app.errorhandler(505)
    def http_version_not_supported(e):
        return render_template("errors/505.html"), 505

    # Simulate a 505 error for testing
    @app.route('/simulate-505')
    def simulate_505():
        abort(505)
        
    
    return app


