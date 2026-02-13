# locust/locustfile.py
from locust import HttpUser, task, between

class GUDLFTTestUser(HttpUser):
    """
    Simulates a user navigating and booking on the GUDLFT application.
    """
    # Setting the base host URL
    host = "http://127.0.0.1:5000"

    # Wait time between tasks: 1 to 5 seconds
    wait_time = between(1, 5)

    def on_start(self):
        """
        Action: Initializes valid data based on your specific JSON files.
        """
        self.club_email = "admin@irontemple.com"
        self.club_name = "Iron Temple"
        self.competition_name = "Fall Classic"

    @task(3)
    def view_index(self):
        """
        Action: GET /
        """
        self.client.get("/")

    @task(2)
    def view_points_board(self):
        """
        User Story: 1 Total Transparency
        Action: GET /pointsDisplay
        """
        self.client.get("/pointsDisplay")

    @task(2)
    def login_and_dashboard(self):
        """
        User Story: 2 Dashboard Access
        Action: POST /showSummary
        """
        self.client.post("/showSummary", data={"email": self.club_email})

    @task(1)
    def full_booking_flow(self):
        """
        User Stories: 3, 4, 5 - Booking Cycle
        Action: Sequential flow from booking page to purchase.
        """
        # Step 1: Access the booking page
        book_url = f"/book/{self.competition_name}/{self.club_name}"
        self.client.get(book_url)

        # Step 2: Submit a purchase
        self.client.post("/purchasePlaces", data={
            "club": self.club_name,
            "competition": self.competition_name,
            "places": 1
        })

    @task(1)
    def logout(self):
        """
        User Story: 6 Session Closure
        Action: GET /logout
        """
        self.client.get("/logout")