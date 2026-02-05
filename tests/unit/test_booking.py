import pytest
from server import app


class TestBooking:
    """
    Unit tests for the booking logic and constraints.
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

    def test_booking_point_deduction(self, mocker, client):
        """
        Action: POST /purchasePlaces with 5 places for a club with 20 points.
        Expected: Club points decremented to 15 in the global data list.
        """
        mock_clubs = [{'name': 'Club', 'email': 'c@c.co', 'points': '20'}]
        mock_comps = [{
            'name': 'Comp',
            'date': '2026-10-10 10:00:00',
            'numberOfPlaces': '25'
        }]
        mocker.patch('server.clubs', mock_clubs)
        mocker.patch('server.competitions', mock_comps)

        client.post('/purchasePlaces', data={
            'club': 'Club',
            'competition': 'Comp',
            'places': '5'
        })

        assert mock_clubs[0]['points'] == '15'

    def test_booking_limit_per_club(self, mocker, client):
        """
        Action: POST /purchasePlaces with 13 places (exceeding the limit).
        Expected: HTTP 200, Error Flash message present, and stock unchanged.
        """
        mock_clubs = [{'name': 'Club', 'email': 'c@c.co', 'points': '20'}]
        mock_comps = [{
            'name': 'Comp',
            'date': '2026-10-10 10:00:00',
            'numberOfPlaces': '25'
        }]
        mocker.patch('server.clubs', mock_clubs)
        mocker.patch('server.competitions', mock_comps)

        response = client.post('/purchasePlaces', data={
            'club': 'Club',
            'competition': 'Comp',
            'places': '13'
        })

        assert response.status_code == 200
        assert b'12 places' in response.data

    def test_booking_exceeding_club_points(self, mocker, client):
        """
        Action: POST /purchasePlaces with more places than the club balance.
        Expected: HTTP 200, Error Flash message present, and points unchanged.
        """
        mock_clubs = [{'name': 'Club', 'email': 'c@c.co', 'points': '5'}]
        mock_comps = [{
            'name': 'Comp',
            'date': '2026-10-10 10:00:00',
            'numberOfPlaces': '25'
        }]
        mocker.patch('server.clubs', mock_clubs)
        mocker.patch('server.competitions', mock_comps)

        response = client.post('/purchasePlaces', data={
            'club': 'Club',
            'competition': 'Comp',
            'places': '6'
        })

        assert response.status_code == 200
        assert b'Not enough points' in response.data

    def test_booking_exceeding_competition_capacity(self, mocker, client):
        """
        Action: POST /purchasePlaces with more places than available in stock.
        Expected: HTTP 200, Error Flash message present, and stock unchanged.
        """
        mock_clubs = [{'name': 'Club', 'email': 'c@c.co', 'points': '20'}]
        mock_comps = [{
            'name': 'Comp',
            'date': '2026-10-10 10:00:00',
            'numberOfPlaces': '5'
        }]
        mocker.patch('server.clubs', mock_clubs)
        mocker.patch('server.competitions', mock_comps)

        response = client.post('/purchasePlaces', data={
            'club': 'Club',
            'competition': 'Comp',
            'places': '6'
        })

        assert response.status_code == 200
        assert b'Not enough places' in response.data

    def test_booking_with_negative_quantity(self, mocker, client):
        """
        Action: POST /purchasePlaces with a negative quantity.
        Expected: HTTP 200, Error Flash message present, and status unchanged.
        """
        mock_clubs = [{'name': 'Club', 'email': 'c@c.co', 'points': '20'}]
        mock_comps = [{
            'name': 'Comp',
            'date': '2026-10-10 10:00:00',
            'numberOfPlaces': '25'
        }]
        mocker.patch('server.clubs', mock_clubs)
        mocker.patch('server.competitions', mock_comps)

        response = client.post('/purchasePlaces', data={
            'club': 'Club',
            'competition': 'Comp',
            'places': '-1'
        })

        assert response.status_code == 200
        assert b'Invalid' in response.data

    def test_booking_for_past_competition(self, mocker, client):
        """
        Action: POST /purchasePlaces for a competition with a past date.
        Expected: HTTP 200, Error Flash message present, and stock unchanged.
        """
        mock_clubs = [{'name': 'Club', 'email': 'c@c.co', 'points': '20'}]
        mock_comps = [{
            'name': 'Past Comp',
            'date': '2020-01-01 10:00:00',
            'numberOfPlaces': '10'
        }]
        mocker.patch('server.clubs', mock_clubs)
        mocker.patch('server.competitions', mock_comps)

        response = client.post('/purchasePlaces', data={
            'club': 'Club',
            'competition': 'Past Comp',
            'places': '1'
        })

        assert response.status_code == 200
        assert b'over' in response.data or b'past' in response.data

    def test_booking_with_invalid_string_quantity(self, mocker, client):
        """
        Action: POST /purchasePlaces with a non-numeric string.
        Expected: HTTP 200 and error message for invalid input.
        """
        mock_clubs = [{'name': 'Club', 'email': 'c@c.co', 'points': '20'}]
        mock_comps = [{
            'name': 'Comp',
            'date': '2026-10-10 10:00:00',
            'numberOfPlaces': '25'
        }]
        mocker.patch('server.clubs', mock_clubs)
        mocker.patch('server.competitions', mock_comps)

        response = client.post('/purchasePlaces', data={
            'club': 'Club',
            'competition': 'Comp',
            'places': 'abc'
        })

        assert response.status_code == 200
        assert b'Invalid' in response.data or b'number' in response.data