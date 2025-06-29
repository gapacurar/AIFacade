from flask_login import current_user

def test_session_protection_on_user_agent_change(client):
    """
    GIVEN an app made for testing
    WHEN trying to log in an user then change the header to another User-Agent in order to trigger session_protection
    CHECK if the login_session_protection works properly.
    """
    # Step 1: Log in with original User-Agent
    with client:
        original_headers = {
        "User-Agent": "Mozilla/5.0 (Original)"
    }


        response = client.post("/register", data={
        "username": "sessionuser",
        "password": "testpass"
    }, headers=original_headers, follow_redirects=True)

        assert b"Account created successfully" in response.data

        response = client.post("/login", data={
        "username": "sessionuser",
        "password": "testpass"
    }, headers=original_headers, follow_redirects=True)

        assert b"AI Web Interface" in response.data  # Assuming successful login shows this
        client.get('/', headers=original_headers) 
        assert current_user.is_authenticated # If the log in is a success then this will be True
        assert current_user.id == 1 # Because we only registered 1 user


    # Step 2: Request with a different User-Agent (simulating hijack)
        hijack_headers = {
        "User-Agent": "MaliciousBot/1.0"
    }

        response = client.get("/", headers=hijack_headers, follow_redirects=True)

        # User should be logged out due to session protection
        assert b"Login" in response.data or b"Please log in" in response.data # The hijacked session wont be able to see the chat
        assert not current_user.is_authenticated # To confirm we are not connected anymore


def test_csp_header(client):
    """
    GIVEN a flask application configured for testing with CSP enabled via @app.after_request

    WHEN we make a get request and check the headers of the response

    CHECK if the CSP exists and see if a line from our CSP there and functional.
    """
    response = client.get('/')
    csp = response.headers.get('Content-Security-Policy')
    assert csp is not None, "CSP header missing"
    assert "default-src 'self'" in csp
    