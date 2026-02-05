# tests/endtoend/test_ui_flows.py
import pytest
import json
from server import app


class TestUIFlows:
    """
    Functional tests covering real end-to-end user journeys.
    Directly uses loaded server data to ensure maximum test execution.
    """

    @pytest.fixture(autouse=True)
    def setup_test_data(self, mocker):
        """
        Action: Load physical test files from tests/data.
        Ensures the server uses the extensive dataset for E2E testing.
        """
        with open('tests/data/clubs.json') as c:
            clubs_data = json.load(c)
        with open('tests/data/competitions.json') as comp:
            comps_data = json.load(comp)

        # Patching server data to use the provided JSON files
        mocker.patch('server.clubs', clubs_data['clubs'])
        mocker.patch('server.competitions', comps_data['competitions'])

    @pytest.fixture
    def client(self):
        """Configure and return the Flask test client."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_story_1_public_scoreboard(self, client):
        """
        Action: GET /pointsDisplay to view the public scoreboard.
        Expected: HTTP 200 and presence of the HTML table structure.
        """
        response = client.get('/pointsDisplay')
        assert response.status_code == 200
        # Check for specific names from your 20-item JSON
        assert b'Simply Lift' in response.data
        assert b'Alpha Training' in response.data

    def test_story_2_and_6_auth_flow(self, client):
        """
        Action: POST /showSummary to login and GET /logout to destroy the
        session.
        Expected: HTTP 200 for logout and session properly cleared.
        """
        client.post(
            '/showSummary',
            data={'email': 'john@simplylift.co'},
            follow_redirects=True
        )
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'Welcome' in response.data

    def test_story_3_booking_success(self, client):
        """
        Action: POST /purchasePlaces with valid data for an existing club
        and competition.
        Expected: HTTP 200 and successful redirection to the summary page.
        """
        client.post('/showSummary', data={'email': 'john@simplylift.co'})
        response = client.post('/purchasePlaces', data={
            'competition': 'Final Showdown',
            'club': 'Simply Lift',
            'places': '1'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Great-booking complete!' in response.data

    def test_story_4_booking_errors(self, client):
        """
        Action: POST /purchasePlaces with values exceeding limits or
        negative quantities.
        Expected: Request processed without server crash (Flash messages
        expected).
        """
        client.post('/showSummary', data={'email': 'rich@test.com'})

        # Case: 13 places (limit is 12)
        res_limit = client.post('/purchasePlaces', data={
            'competition': 'Final Showdown',
            'club': 'Rich Club',
            'places': '13'
        }, follow_redirects=True)
        assert b"can't book more than 12" in res_limit.data

        # Case: Negative places
        res_neg = client.post('/purchasePlaces', data={
            'competition': 'Final Showdown',
            'club': 'Rich Club',
            'places': '-1'
        }, follow_redirects=True)
        assert b"positive number" in res_neg.data

    def test_story_4_bis_insufficient_points(self, client):
        """
        Action: POST /purchasePlaces with more points than the club has.
        Expected: Flash message 'Not enough points'.
        """
        client.post('/showSummary', data={'email': 'zero@test.com'})
        response = client.post('/purchasePlaces', data={
            'competition': 'Final Showdown',
            'club': 'Club Zero',
            'places': '1'
        }, follow_redirects=True)
        assert b"Not enough points" in response.data

    def test_story_5_past_events_access(self, client):
        """
        Action: GET /book/competition/club for a competition with a past date.
        Expected: HTTP 200 and logic handled by the server (Already passed).
        """
        client.post('/showSummary', data={'email': 'john@simplylift.co'})
        response = client.get(
            '/book/Spring%20Festival/Simply%20Lift',
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b"already passed" in response.data

    def test_error_pages_and_invalid_data(self, client):
        """
        Action: Access routes with unknown email or non-existent
        competition names.
        Expected: Server handles missing data gracefully via redirects or
        error messages.
        """
        # Branch: Unknown email
        res_email = client.post(
            '/showSummary',
            data={'email': 'unknown@test.com'},
            follow_redirects=True
        )
        assert b"Unknown email" in res_email.data

        # Branch: Unknown competition
        res_comp = client.get(
            '/book/NonExistent/Simply%20Lift',
            follow_redirects=True
        )
        assert b"Something went wrong" in res_comp.data