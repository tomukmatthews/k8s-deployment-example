from random import randint

from locust import HttpUser, constant, task


class LoadTest(HttpUser):
    wait_time = constant(0)
    host = "http://fastapi-app.com"

    @task
    def index(self):
        self.client.get("/")

    @task
    def predict_batch_1(self):
        request_body = {"values": [randint(1, 1000) for i in range(randint(1, 1000))]}
        self.client.post(f"{self.host}/entropy", json=request_body)
