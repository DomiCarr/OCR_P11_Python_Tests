# tests/integration/test_server_routes.py
import pytest
from server import app


class TestServerRoutes:
    """
    Integration test suite for server route accessibility.
    Validates HTTP response codes and template rendering for all endpoints.
    """

    @pytest.fixture
    def client(self):
        """
        Action: Initializes the Flask test client.
        Expected: Returns a client for simulating HTTP requests across the app.
        """
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_index_route(self, client):
        """
        Action: GET /.
        Expected: HTTP 200 and presence of the registration portal title.
        """
        response = client.get('/')
        assert response.status_code == 200
        assert b'Welcome to the GUDLFT Registration Portal' in response.data

    def test_points_display_route(self, client):
        """
        Action: GET /pointsDisplay.
        Expected: HTTP 200 (Public access according to Phase 2 specifications).
        """
        response = client.get('/pointsDisplay')
        assert response.status_code == 200

    def test_unknown_route(self, client):
        """
        Action: GET /non_existent_route.
        Expected: HTTP 404 (Standard error handling).
        """
        response = client.get('/non_existent_route')
        assert response.status_code == 404

    def test_booking_route_with_invalid_parameters(self, mocker, client):
        """
        Action: GET /book/InvalidComp/InvalidClub.
        Expected: HTTP 404 status code for non-existent resources.
        """
        mocker.patch('server.clubs', [])
        mocker.patch('server.competitions', [])

        response = client.get('/book/UnknownComp/UnknownClub')

        assert response.status_code == 404

    def test_logout_redirect(self, client):
        """
        Action: GET /logout.
        Expected: HTTP 302 redirecting to the index page.
        """
        response = client.get('/logout', follow_redirects=False)
        assert response.status_code == 302
        assert response.location == '/' or response.location == 'http://localhost/'