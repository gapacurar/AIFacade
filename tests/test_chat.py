from flask_login import current_user
from unittest.mock import patch

def test_redirect_home(client):
    """
    GIVEN a client already configured for testing
    WHEN we try to connect to index.html without being connected
    CHECK if we get redirected to the login page.
    """
    with client:
        response = client.get('/', follow_redirects=True)
        assert response.status_code == 200
        assert response.request.path == '/login'


def test_prompt_no_message(client, auth):
    """
    GIVEN a client already configured for testing
    WHEN we try post without any characters in the prompt
    CHECK if we receive the flash message after being redirected back to the page.
    """
    with client:
        auth.login()
        assert current_user.is_authenticated
        response = client.post('/chat', data={"prompt": ''}, follow_redirects = True)
        assert response.status_code == 200
        assert b"Please enter a message" in response.data





def test_answer(client, auth):
    """
    GIVEN a client already configured for testing, an authenticated user and a prompt
    
    WHEN we try to prompt deepseek for a response
    
    CHECK if we get an 402 ERROR. That means the request was successfully sent and we received a response.

   
    We can only test for 402 ERRORS because it's required to pay for the API to work, but a 402 would mean a success.
    
    NOTE: We also have the "or 401" in assert because we will use a fake env key for the .env file. When you will use a real API Key just remove that line.
    
    NOTE: If you add funds into your deepseek DONT use Error 402 in assert anymore
    """
    with client:
        auth.login()
        prompt = 'Hello'
        response = client.post('/chat', data={"prompt": prompt}, follow_redirects = True)
        assert response.status_code == 200
        assert b"API Error 402: Insufficient Balance" in response.data or b"API Error 401: Authentication Fails" in response.data


def test_clear_chat(client, auth):
    """
    Given a prompt made in chat, an user authenticated and a client for testing

    WHEN we attend to clear the chat history

    CHECK if we receive the flash message and if the response was deleted from the history. 

    NOTE: We also have the "or 401" in assert because we will use a fake env key for the .env file. When you will use a real API Key just remove that line.
    
    NOTE: If you add funds into your deepseek DONT use Error 402 in assert anymore
    """
    with client:
        auth.login()
        prompt = 'Hello'
        response = client.post('/chat', data={"prompt": prompt}, follow_redirects = True)
        assert b"API Error 402: Insufficient Balance" in response.data or b"API Error 401: Authentication Fails" in response.data

        response = client.post('/clear', follow_redirects = True)
        assert response.status_code == 200
        assert b"Chat history cleared" in response.data
        assert b"API Error 402: Insufficient Balance" not in response.data or b"API Error 401: Authentication Fails" not in response.data


def test_prompt_too_long(client, auth):
    """
    GIVEN a client already configured for testing and an authenticated user

    WHEN trying to use a prompth with a lenght of 1000+ characters

    CHECK if we get the correct error.
    """
    auth.login()
    prompt = 'a' * 1001
    response = client.post('/chat', data={"prompt": prompt}, follow_redirects = True)
    assert b"Prompt too long." in response.data


def test_chat_view_handles_exception(client, auth, app):
    auth.login()  # Log in a user so current_user is valid

    with patch("project.chat.query_deepseek", side_effect=Exception("test error")):
        response = client.post("/chat", data={"prompt": "This will cause error"}, follow_redirects=True)

        # Check if redirected to home
        assert response.status_code == 200
        assert b"Something went wrong." in response.data



def test_query_deepseek_exception_handling(client, auth):
    """
    GIVEN a working Flask test client and an authenticated user,
    WHEN the DeepSeek API raises an unexpected exception (e.g., connection error),
    THEN the query_deepseek should handle it gracefully and return an error string.
    """

    auth.login()

    # Patch 'requests.post' to raise a generic Exception
    with patch("project.utils.requests.post", side_effect=Exception("Test exception")):
        response = client.post("/chat", data={"prompt": "trigger error"}, follow_redirects=True)

        assert response.status_code == 200
        # Since the function returns "Error: <exception message>"
        assert b"Error: Test exception" in response.data or b"Something went wrong." in response.data
