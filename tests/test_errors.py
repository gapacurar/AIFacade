

def test_error_404_handling(client):
    """
    GIVEN a flask app alreadyh configured for testing
    WHEN a bad url gets requested
    THEN check if it properly
    """
    with client:
        response = client.get('/deeepseek')
        assert response.status_code == 404
        assert b"Oops! Page not found..." in response.data

def test_erorr_505_handling(client):
    """
    GIVEN a flask app already configured for testing
    WHEN simulating a 505 error
    THEN check if the error handler is rendering the 505.html properly
    """

    with client:
        response = client.get('/simulate-505')
        assert response.status_code == 505
        assert b"Something went wrong on our end. We're working to fix it!" in response.data
        # check for back home button
        assert b"Go Back Home" in response.data

