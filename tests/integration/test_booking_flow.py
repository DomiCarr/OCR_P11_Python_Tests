import pytest
from server import app


class TestBookingFlow:
    """
    Integration test suite for the booking process.
    Validates the continuity between login, booking, and data persistence.
    """

    @pytest.fixture
    def client(self):
        """
        Action: Initializes the Flask test client.
        Expected: Returns a client for simulating a sequence of HTTP requests.
        """
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_complete_booking_flow(self, mocker, client):
        """
        Action: Follows the sequence Login -> Access Booking -> Purchase.
        Expected: HTTP 200 and points updated in the shared state.
        """
        mock_clubs = [{
            'name': 'Iron Temple',
            'email': 'admin@irontemple.com',
            'points': '20'
        }]
        mock_comps = [{
            'name': 'Spring Festival',
            'date': '2026-03-27 10:00:00',
            'numberOfPlaces': '25'
        }]
        mocker.patch('server.clubs', mock_clubs)
        mocker.patch('server.competitions', mock_comps)

        # 1. Login
        login_res = client.post(
            '/showSummary',
            data={'email': 'admin@irontemple.com'},
            follow_redirects=True
        )
        assert login_res.status_code == 200
        assert b'Welcome, admin@irontemple.com' in login_res.data

        # 2. Access Booking Page
        book_res = client.get('/book/Spring Festival/Iron Temple')
        assert book_res.status_code == 200
        assert b'Booking for Spring Festival' in book_res.data

        # 3. Purchase Places
        purchase_res = client.post('/purchasePlaces', data={
            'club': 'Iron Temple',
            'competition': 'Spring Festival',
            'places': '5'
        }, follow_redirects=True)

        # 4. Final Verifications
        assert purchase_res.status_code == 200
        assert b'Great-booking complete!' in purchase_res.data
        assert mock_clubs[0]['points'] == '15'
        assert mock_comps[0]['numberOfPlaces'] == '20'

    def test_booking_persistence_on_points_board(self, mocker, client):
        """
        Action: Purchase places and then access the public points board.
        Expected: Updated points balance is visible on the public display.
        """
        mock_clubs = [{
            'name': 'Iron Temple',
            'email': 'admin@irontemple.com',
            'points': '10'
        }]
        mock_comps = [{
            'name': 'Fall Classic',
            'date': '2026-10-22 13:30:00',
            'numberOfPlaces': '13'
        }]
        mocker.patch('server.clubs', mock_clubs)
        mocker.patch('server.competitions', mock_comps)

        # Execute Purchase
        client.post('/purchasePlaces', data={
            'club': 'Iron Temple',
            'competition': 'Fall Classic',
            'places': '2'
        })

        # Check Public Board (Phase 2 Requirement)
        board_res = client.get('/pointsDisplay')
        assert board_res.status_code == 200
        assert b'Iron Temple' in board_res.data
        assert b'8' in board_res.data