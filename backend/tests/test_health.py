import unittest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app


class TestHealthEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_root_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "online")
        self.assertEqual(data["service"], "ai-sight-reader-backend")
        self.assertIn("documentation", data)

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["service"], "ai-sight-reader-backend")

    @patch("app.api.endpoints.adk_composer_engine.generate_sight_reading_exercise", new_callable=AsyncMock)
    def test_stream_reasoning_engine(self, mock_generate):
        mock_generate.return_value = {
            "abc_notation": "X:1\nM:4/4\nK:C\nC4|]",
            "token_usage": 100,
            "estimated_cost_usd": 0.0001
        }
        response = self.client.post(
            "/api/stream_reasoning_engine",
            json={"class_method": "stream_query", "input": {"difficulty": "beginner"}}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("abc_notation", response.text)

    @patch("app.api.endpoints.adk_composer_engine.generate_sight_reading_exercise", new_callable=AsyncMock)
    def test_reasoning_engine(self, mock_generate):
        mock_generate.return_value = {
            "abc_notation": "X:1\nM:4/4\nK:C\nC4|]",
            "token_usage": 100,
            "estimated_cost_usd": 0.0001
        }
        response = self.client.post(
            "/api/reasoning_engine",
            json={"class_method": "query", "input": {"difficulty": "beginner"}}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("output", data)
        self.assertIn("abc_notation", data["output"])


if __name__ == "__main__":
    unittest.main()

