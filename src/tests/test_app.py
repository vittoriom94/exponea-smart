import pytest
from fastapi.testclient import TestClient

import tests.utils
from app import app


@pytest.fixture
def non_mocked_hosts() -> list:
    return ["testserver"]


class TestApp:
    client = TestClient(app)

    def test_success(self, httpx_mock):
        httpx_mock.add_response(status_code=200, json={"time": 1})

        response = self.client.get("/api/smart", params={"timeout": 500})
        assert response.status_code == 200
        assert response.json()["time"] < 500

    def test_first_fails_second_success(self, httpx_mock):
        httpx_mock.add_callback(tests.utils.unavailable_endpoint)
        httpx_mock.add_response(status_code=200, json={"time": 1})
        httpx_mock.add_response(status_code=200, json={"time": 1})

        response = self.client.get("/api/smart", params={"timeout": 500})
        assert response.status_code == 200
        assert response.json()["time"] < 500

        httpx_mock.add_callback(tests.utils.unavailable_endpoint)
        httpx_mock.add_callback(tests.utils.unavailable_endpoint)
        httpx_mock.add_response(status_code=200, json={"time": 1})

        response = self.client.get("/api/smart", params={"timeout": 500})
        assert response.status_code == 200
        assert response.json()["time"] < 500

        httpx_mock.add_callback(tests.utils.unavailable_endpoint)
        httpx_mock.add_response(status_code=200, json={"time": 1})
        httpx_mock.add_callback(tests.utils.unavailable_endpoint)

        response = self.client.get("/api/smart", params={"timeout": 500})
        assert response.status_code == 200
        assert response.json()["time"] < 500

    def test_success_when_first_timeout(self, httpx_mock):
        httpx_mock.add_callback(tests.utils.slow_endpoint)
        httpx_mock.add_response(status_code=200, json={"time": 1})
        httpx_mock.add_callback(tests.utils.unavailable_endpoint)

        response = self.client.get("/api/smart", params={"timeout": 500})
        assert response.status_code == 200
        assert response.json()["time"] < 500

        httpx_mock.add_callback(tests.utils.slow_endpoint)
        httpx_mock.add_callback(tests.utils.slow_endpoint)
        httpx_mock.add_response(status_code=200, json={"time": 1})

        response = self.client.get("/api/smart", params={"timeout": 500})
        assert response.status_code == 200
        assert response.json()["time"] < 500

        httpx_mock.add_callback(tests.utils.unavailable_endpoint)
        httpx_mock.add_callback(tests.utils.slow_endpoint)
        httpx_mock.add_response(status_code=200, json={"time": 1})

        response = self.client.get("/api/smart", params={"timeout": 500})
        assert response.status_code == 200
        assert response.json()["time"] < 500

    def test_fail_for_timeout(self, httpx_mock):
        httpx_mock.add_callback(tests.utils.slow_endpoint)
        httpx_mock.add_callback(tests.utils.slow_endpoint)
        httpx_mock.add_callback(tests.utils.slow_endpoint)

        response = self.client.get("/api/smart", params={"timeout": 500})
        assert response.status_code == 503

    def test_fail_for_unavailable(self, httpx_mock):

        httpx_mock.add_callback(tests.utils.unavailable_endpoint)
        httpx_mock.add_callback(tests.utils.unavailable_endpoint)
        httpx_mock.add_callback(tests.utils.unavailable_endpoint)

        response = self.client.get("/api/smart", params={"timeout": 500})
        assert response.status_code == 503
