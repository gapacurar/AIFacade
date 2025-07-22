"""
This module contains pytest fixtures and helper classes for testing the Flask application.
Fixtures:
---------
- app:
    Creates and configures a new Flask app instance for each test module.
    Uses a temporary SQLite database file for isolation.
    Sets up the app with test-specific configuration options (e.g., disables CSRF, rate limiting).
    Ensures all database tables are created before tests and cleans up resources after tests.
- client:
    Provides a Flask test client for sending HTTP requests to the app during tests.
- runner:
    Provides a Flask CLI runner for invoking custom command-line commands in tests.
- auth:
    Provides an instance of AuthActions, a helper class for performing authentication actions (register, login, logout) in tests.
- user:
    Provides a new instance of the User model for use in tests.
Classes:
--------
- AuthActions:
    Helper class to encapsulate common authentication actions for tests.
    Methods:
        - register(username='test', password='test'):
            Registers a new user with the given credentials.
        - login(username='test', password='test'):
            Registers (if needed) and logs in a user with the given credentials.
        - logout():
            Logs out the currently authenticated user.
Usage:
------
Import these fixtures in your test modules to easily set up the app context, database, and perform authentication actions.
"""

from project.models import User
# User: The User model, used for creating user instances in tests

import tempfile
# tempfile: Used to create a temporary file for the test database

from project import create_app
# create_app: Factory function to create a Flask app instance for testing

import os
# os: Used for file operations, such as removing the temporary database file

from project.db import db
# db: SQLAlchemy database instance for creating and dropping tables during tests

import pytest
# pytest: Testing framework used for fixtures and test discovery

# Fixture to create and configure a new app instance for each test module
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

# Fixture to provide a test client for the app
@pytest.fixture
def client(app):
    return app.test_client()

# Fixture to provide a CLI runner for the app
@pytest.fixture
def runner(app):
    return app.test_cli_runner()

# Helper class to perform authentication actions in tests
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
    
# Fixture to provide authentication actions in tests
@pytest.fixture
def auth(client):
    return AuthActions(client)

# Fixture to provide a User instance
@pytest.fixture
def user():
    return User()
