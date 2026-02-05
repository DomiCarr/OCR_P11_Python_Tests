# tests/unit/test_points_board.py
import pytest
from server import app


class TestPointsBoard:
    """
    Test suite for the public points display (Phase 2).
    Validates that the leaderboard is accessible and displays correct data.
    """

    @pytest.fixture
    def client(self):
        """
        Action: Initializes the Flask test client.
        Expected: Returns a client for simulating HTTP requests.
        """
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_points_board_accessibility(self, client):
        """
        Action: GET /pointsDisplay without any authentication.
        Expected: HTTP 200 (Publicly accessible route).
        """
        response = client.get('/pointsDisplay')
        assert response.status_code == 200

    def test_points_board_data_rendering(self, mocker, client):
        """
        Action: GET /pointsDisplay with a specific set of mocked club data.
        Expected: HTML contains the exact names and points of all clubs in the data source.
        """
        mock_clubs = [
            {'name': 'Iron Temple', 'email': 'admin@iron.co', 'points': '15'},
            {'name': 'She Lifts', 'email': 'admin@she.co', 'points': '12'}
        ]
        mocker.patch('server.clubs', mock_clubs)

        response = client.get('/pointsDisplay')

        # Verify both clubs are listed with their correct point totals
        assert b'Iron Temple' in response.data
        assert b'15' in response.data
        assert b'She Lifts' in response.data
        assert b'12' in response.data