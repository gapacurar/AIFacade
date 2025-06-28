
def test_session_protection_on_user_agent_change(app, client, auth):
    """
    GIVEN an app made for testing
    WHEN trying to log in an user then change the header to another User-Agent
    CHECK if the login_session_protection works properly.
    """
    # Step 1: Log in with original User-Agent
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

    # Step 2: Request with a different User-Agent (simulating hijack)
    hijack_headers = {
        "User-Agent": "MaliciousBot/1.0"
    }

    response = client.get("/", headers=hijack_headers, follow_redirects=True)

    # User should be logged out due to session protection
    assert b"Login" in response.data or b"Please log in" in response.data