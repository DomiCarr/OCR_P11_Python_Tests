# locustfile.py

from locust import HttpUser, task, between


class ProjectUser(HttpUser):
    # Simulation of a user waiting 1 to 2 seconds between actions
    wait_time = between(1, 2)

    @task
    def access_index(self):
        # Access the home page
        self.client.get("/")