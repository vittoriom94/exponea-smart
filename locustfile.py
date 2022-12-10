import random

from locust import HttpUser, task


class ExponeaUser(HttpUser):
    @task
    def api_smart(self):
        timeout = random.randint(500, 1000)
        with self.client.get("/api/smart", params={"timeout": timeout}, catch_response=True) as response:
            if response.status_code == 503:
                response.success()
            if response.status_code == 200 and timeout < response.json()["time"]:
                response.failure(f"Execution time higher than timeout. [timeout={timeout}, execution-time={response.json()['time']}")



