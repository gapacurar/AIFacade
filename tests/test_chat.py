from flask_login import current_user

def test_redirect_home(client):
    """
    GIVEN a client already configured for testing
    WHEN we try to connect to index.html without being connected
    CHECK if we get the error from flash
    """
    with client:
        response = client.get('/', follow_redirects=False)
        assert response.status_code == 302


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
