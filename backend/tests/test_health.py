import json
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
    def test_stream_reasoning_engine_gemini_enterprise_contract(self, mock_generate):
        mock_generate.return_value = {
            "abc_notation": "X:1\nT:Flute Exercise\nM:4/4\nK:G\nG2 B2 d2 g2 | f2 d2 z2 G2 | c2 e2 d2 B2 | A4 G2 z2 |]",
            "token_usage": 150,
            "estimated_cost_usd": 0.00015
        }
        # Simulate exact Gemini Enterprise request structure with request_json string
        ge_request = {
            "class_method": "streaming_agent_run_with_events",
            "input": {
                "request_json": json.dumps({
                    "message": {
                        "role": "user",
                        "parts": [{"text": "Compose an intermediate flute exercise in G major with 4 bars"}]
                    },
                    "user_id": "user_ge_123",
                    "session_id": "session_ge_456"
                })
            }
        }
        response = self.client.post("/api/stream_reasoning_engine", json=ge_request)
        self.assertEqual(response.status_code, 200)
        
        # Verify that the response is valid JSON-L and contains top-level 'events' list for GE
        lines = [line.strip() for line in response.text.strip().split("\n") if line.strip()]
        self.assertGreaterEqual(len(lines), 1)
        
        first_event = json.loads(lines[0])
        self.assertIn("events", first_event, "Gemini Enterprise contract requires top-level 'events' array")
        self.assertEqual(first_event["session_id"], "session_ge_456")
        self.assertEqual(len(first_event["events"]), 1)
        
        adk_event = first_event["events"][0]
        self.assertEqual(adk_event["author"], "sight_reading_composer")
        self.assertIn("content", adk_event)
        self.assertIn("parts", adk_event["content"])
        self.assertIn("G2 B2 d2 g2", adk_event["content"]["parts"][0]["text"])

    @patch("app.api.endpoints.adk_composer_engine.generate_sight_reading_exercise", new_callable=AsyncMock)
    def test_stream_reasoning_engine_vertex_sdk_contract(self, mock_generate):
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
        self.assertIn("events", data)
        self.assertIn("abc_notation", data["output"])


if __name__ == "__main__":
    unittest.main()


