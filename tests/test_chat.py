import pytest
from flask_login import current_user
from unittest.mock import patch


def test_redirect_home(client):
    """
    GIVEN an unauthenticated user
    WHEN accessing the home route (/)
    THEN the user is redirected to the login page
    """
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'


def test_prompt_no_message(client, auth):
    """
    GIVEN an authenticated user
    WHEN submitting an empty prompt
    THEN a flash error is shown
    """
    auth.login()
    response = client.post('/chat', data={"prompt": ''}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Prompt cannot be empty." in response.data
    assert b"Value error" in response.data


def test_prompt_too_long(client, auth):
    """
    GIVEN an authenticated user
    WHEN submitting a prompt longer than 1000 characters
    THEN an appropriate error is flashed
    """
    auth.login()
    prompt = 'a' * 1001
    response = client.post('/chat', data={"prompt": prompt}, follow_redirects=True)
    assert response.status_code == 200
    assert b"String should have at most 1000 characters" in response.data


def test_answer_from_api_error(client, auth):
    """
    GIVEN a valid user prompt
    WHEN DeepSeek returns a 402 or 401
    THEN the error should appear in the rendered template
    """
    auth.login()
    prompt = 'Hello'
    response = client.post('/chat', data={"prompt": prompt}, follow_redirects=True)
    assert response.status_code == 200
    assert (
        b"API Error 402: Insufficient Balance" in response.data or 
        b"API Error 401: Authentication Fails" in response.data
    )


def test_clear_chat(client, auth):
    """
    GIVEN a prompt was submitted and recorded
    WHEN clearing chat history
    THEN chat history should be removed and flash success should show
    """
    auth.login()

    # Submit chat first
    client.post('/chat', data={"prompt": "Hello"}, follow_redirects=True)

    # Clear chat
    response = client.post('/clear', follow_redirects=True)
    assert response.status_code == 200
    assert b"Chat history cleared" in response.data

    # Verify no chats are present
    assert (
        b"API Error 402: Insufficient Balance" not in response.data and 
        b"API Error 401: Authentication Fails" not in response.data
    )


def test_chat_view_handles_exception(client, auth):
    """
    GIVEN the chat endpoint
    WHEN an internal exception occurs during processing
    THEN a user-friendly error is shown and no crash happens
    """
    auth.login()

    with patch("project.chat.query_deepseek", side_effect=Exception("test error")):
        response = client.post("/chat", data={"prompt": "This will cause error"}, follow_redirects=True)
        assert response.status_code == 200
        assert b"Something went wrong while saving the chat." in response.data


def test_query_deepseek_exception_handling(client, auth):
    """
    GIVEN the DeepSeek API call
    WHEN a request-level exception is raised (e.g., timeout, network error)
    THEN it should be handled gracefully without crashing
    """
    auth.login()

    with patch("project.utils.requests.post", side_effect=Exception("Test exception")):
        response = client.post("/chat", data={"prompt": "trigger error"}, follow_redirects=True)
        assert response.status_code == 200
        assert b"Error: Test exception" in response.data or b"Something went wrong." in response.data
