"""Tests for PlagiSense FastAPI foundation endpoints."""

import unittest
from fastapi.testclient import TestClient

from backend.main import app


class TestFastAPIFoundation(unittest.TestCase):
    """Test suite for FastAPI health check, docs, and CORS configuration."""

    def setUp(self):
        self.client = TestClient(app)

    def test_health_check_endpoint(self):
        """Test GET /health returns 200 OK and expected JSON payload."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "ok",
                "service": "PlagiSense API",
            },
        )

    def test_docs_endpoint(self):
        """Test GET /docs returns 200 OK with Swagger UI HTML."""
        response = self.client.get("/docs")
        self.assertEqual(response.status_code, 200)
        self.assertIn("swagger", response.text.lower())

    def test_openapi_json(self):
        """Test GET /openapi.json returns valid schema with PlagiSense API title."""
        response = self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)
        schema = response.json()
        self.assertEqual(schema["info"]["title"], "PlagiSense API")

    def test_cors_headers_allowed_origin(self):
        """Test that requests with allowed origin receive appropriate CORS header."""
        allowed_origin = "http://localhost:5173"
        response = self.client.options(
            "/health",
            headers={
                "Origin": allowed_origin,
                "Access-Control-Request-Method": "GET",
            },
        )
        self.assertEqual(response.headers.get("access-control-allow-origin"), allowed_origin)


if __name__ == "__main__":
    unittest.main()
