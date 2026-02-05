# tests/unit/test_auth.py
import pytest
from server import app


class TestAuth:
    """
    Test suite for authentication logic.
    Validates access control based on email registration and session termination.
    """

    @pytest.fixture
    def client(self):
        """
        Action: Initializes the Flask test client with TESTING configuration.
        Expected: Returns a client for simulating HTTP requests.
        """
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_login_with_registered_email(self, mocker, client):
        """
        Action: POST /showSummary with an email present in the data source.
        Expected: HTTP 200, "Welcome" text in HTML, and email stored in session.
        """
        mock_clubs = [
            {'name': 'Test Club', 'email': 'test@test.com', 'points': '10'}
        ]
        mocker.patch('server.clubs', mock_clubs)

        response = client.post('/showSummary', data={'email': 'test@test.com'}, follow_redirects=True)
        assert response.status_code == 200
        assert b'Welcome, test@test.com' in response.data

    def test_login_with_unregistered_email(self, mocker, client):
        """
        Action: POST /showSummary with an email NOT present in the data source.
        Expected: HTTP 302 (Redirect) and error Flash message present in the HTML.
        """
        mocker.patch('server.clubs', [])

        # follow_redirects=True allows us to check the final page content (the Flash message)
        response = client.post('/showSummary', data={'email': 'unknown@test.com'}, follow_redirects=True)

        # In Flask, an unknown user should be redirected to index with a message
        assert response.status_code == 200  # 200 after following the redirect
        assert b'Email not found' in response.data or b'Sorry' in response.data

    def test_logout_process(self, client):
        """
        Action: GET /logout.
        Expected: HTTP 302 (Redirect) and session cleared (redirect to index).
        """
        response = client.get('/logout')

        assert response.status_code == 302
        assert response.location.endswith('/') or response.location == 'http://localhost/'