import pytest
from project.models import User
import tempfile
from project import create_app
import os
from project.db import db


@pytest.fixture(scope='module')
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({'TESTING': True, 
                      'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}', 
                      'SQLALCHEMY_TRACK_MODIFICATIONS': False,
                      'WTF_CSRF_ENABLED': False})

    with app.app_context():
        db.create_all()  

    yield app

    with app.app_context():
        db.session.remove()
        for engine in db.engines.values():
            engine.dispose()

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self._client = client
    
    def register(self, username='test', password='test'):
        return self._client.post('/register', data={
                                                'username':username,
                                                'password':password
        })

    def login(self, username='test', password='test'):
        self.register()
        return self._client.post('/login',
                                 data={'username': username,
                                       'password': password}
    )
    def logout(self):
        return self._client.get('/logout')
    
@pytest.fixture
def auth(client):
    return AuthActions(client)

@pytest.fixture
def user():
    return User()
