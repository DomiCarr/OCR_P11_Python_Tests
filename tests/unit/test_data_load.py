# tests/unit/test_data_load.py
import server


class TestDataLoad:
    """
    Test suite for JSON data loading.
    Validates that external files are parsed into correct Python types and structures.
    """

    def test_clubs_loading_type(self):
        """
        Action: Executes loadClubs() function.
        Expected: Returned object is a list (required for iteration in templates).
        """
        clubs = server.loadClubs()
        assert isinstance(clubs, list)

    def test_competitions_loading_type(self):
        """
        Action: Executes loadCompetitions() function.
        Expected: Returned object is a list (required for filtering in routes).
        """
        competitions = server.loadCompetitions()
        assert isinstance(competitions, list)

    def test_club_required_keys(self):
        """
        Action: Inspects the keys of the first element in the club list.
        Expected: Keys 'name', 'email', and 'points' exist (prevents KeyError).
        """
        clubs = server.loadClubs()
        if len(clubs) > 0:
            club = clubs[0]
            assert 'name' in club
            assert 'email' in club
            assert 'points' in club

    def test_competition_required_keys(self):
        """
        Action: Inspects the keys of the first element in the competition list.
        Expected: Keys 'name', 'date', and 'numberOfPlaces' exist (required for booking logic).
        """
        competitions = server.loadCompetitions()
        if len(competitions) > 0:
            comp = competitions[0]
            assert 'name' in comp
            assert 'date' in comp
            assert 'numberOfPlaces' in comp