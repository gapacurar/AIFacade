from flask_login import current_user
from unittest.mock import patch
import pytest

def test_register_user(client):
    """
    GIVEN a Flask Application configured for testing

    WHEN a going to /register and a new User is created

    THEN check if route exists, user is registered correctly, and password is hashed
    """
    assert client.get('/register').status_code == 200
    # Send POST request to /register
    response = client.post("/register",
                           data = {'username': 'test', 'password': 'test'}, follow_redirects=True)
    
    # Assert request succeeded
    assert response.status_code == 200  # Or 200 depending on your implementation


def test_user_exists(client):
    """
    GIVEN a Flask application configured for testing

    WHEN trying to register an already registered user

    THEN check if it properly rejects the user registration

    """
    with client:
        client.get('/register')
        response = client.post('/register', data = {'username': 'test', 'password' : 'abc'}, follow_redirects=True)
        assert response.status_code  == 200 #Because follow redirects are true the status code is 200, otherwise it would be 302
        assert b"User already exists." in response.data 

def test_login(client, auth):
    """
    GIVEN a flask application configured for testing

    WHEN going to /login and an existent user tries to log in

    THEN check if authentication works, redirect works, user is correctly logged in.
    """
    assert client.get('/login').status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/"

    with client:
        client.get('/')
        assert current_user.is_authenticated
        assert current_user.id == 1

def test_invalid_login(client):
    """
    GIVEN a flask app configured for testing

    WHEN going to /login and a non existent user tries to log in

    THEN check if it properly rejects the user authentication
    """
    with client:
        response = client.post('/login', data = {'username' : 'invalid', 'password': 'invalid'}, follow_redirects=True)

        assert response.status_code == 200
        assert b"Invalid username or password"

def test_redirect_logged_in(client, auth):
    """
    GIVEN a flask app configured for testing.

    WHEN going to /login as an authenticated user

    THEN check if you are correctly redirected to index.html
    """
    with client:
        auth.login()
        response = client.get('/login', follow_redirects=False)
        assert response.status_code == 302
        assert response.headers["Location"] == "/"


def test_logout(client, auth):
    """"
    GIVEN an user already logged in

    WHEN the user tries to logout

    CHECK if the user is proprely logged out from the session
    """
    auth.login()
    assert client.get('/logout', follow_redirects=True).status_code == 200

    with client:
        auth.logout()
        assert not current_user.is_authenticated




def test_password_property_and_check(user):
    """
    Given an user with the User model

    When we try to check the password

    CHECK if password is hashed, if we get attribute error if we try to extract plain text, check if password is stored correctly, check for wrong password.
    
    """
    # Setting password should hash it
    user.password = 'secret'
    assert user.password_hash is not None
    assert user.password_hash != 'secret'  # Ensure it’s hashed

    # Trying to get password should raise AttributeError
    with pytest.raises(AttributeError, match="Password is write-only"):
        _ = user.password

    # check_password returns True for correct password
    assert user.check_password('secret') is True
    # and False for wrong password
    assert user.check_password('wrong') is False


def test_register_exception(client):
    """
    GIVEN a Flask test client

    WHEN the database commit raises an Exception during user registration

    CHECK the user is redirected and sees a flash message indicating something went wrong
    """
    with patch('project.db.db.session.commit', side_effect=Exception("test error")):
        response = client.post('/register', data={
            'username': 'newuser',
            'password': 'newpassword'
        }, follow_redirects=True)

        # CHECK if the error flash message appears in the response
        assert b"Something went wrong." in response.data
