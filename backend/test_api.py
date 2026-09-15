"""Tests for PlagiSense FastAPI endpoints including document upload and NLP analysis."""

import io
import unittest
import docx
from fastapi.testclient import TestClient

from backend.main import app
from backend.test_document_parser import _create_minimal_pdf


def _create_docx_bytes(paragraphs: list[str]) -> bytes:
    """Create in-memory DOCX bytes with given paragraphs."""
    doc = docx.Document()
    for p in paragraphs:
        doc.add_paragraph(p)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


class TestFastAPIFoundationAndAnalyze(unittest.TestCase):
    """Test suite for FastAPI endpoints: /health, /docs, CORS, and POST /analyze with NLP integration."""

    def setUp(self):
        self.client = TestClient(app)

    # --- FOUNDATION ENDPOINT TESTS ---

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

    # --- POST /analyze TESTS ---

    def test_analyze_txt_plus_txt(self):
        """Test POST /analyze with two TXT documents returning real NLP analysis."""
        source_content = b"Regular exercise improves cardiovascular health."
        sub_content = b"Regular exercise improves cardiovascular health."

        response = self.client.post(
            "/analyze",
            files={
                "source_file": ("source.txt", io.BytesIO(source_content), "text/plain"),
                "submission_file": ("submission.txt", io.BytesIO(sub_content), "text/plain"),
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("overall_score", data)
        self.assertIn("overall_risk", data)
        self.assertIn("semantic_similarity", data)
        self.assertIn("lexical_similarity", data)
        self.assertIn("concept_overlap", data)
        self.assertIn("suspicious_passages", data)
        self.assertIn("overall", data)
        self.assertIn("matches", data)
        self.assertIsInstance(data["matches"], list)
        self.assertGreaterEqual(data["overall_score"], 0.8)

    def test_analyze_pdf_plus_pdf(self):
        """Test POST /analyze with two PDF documents."""
        source_pdf = _create_minimal_pdf(["Regular exercise improves cardiovascular health."])
        sub_pdf = _create_minimal_pdf(["Frequent physical activity helps maintain a healthy heart."])

        response = self.client.post(
            "/analyze",
            files={
                "source_file": ("source.pdf", io.BytesIO(source_pdf), "application/pdf"),
                "submission_file": ("submission.pdf", io.BytesIO(sub_pdf), "application/pdf"),
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("overall_score", data)
        self.assertIn("overall_risk", data)
        self.assertIn("matches", data)

    def test_analyze_docx_plus_docx(self):
        """Test POST /analyze with two DOCX documents."""
        source_docx = _create_docx_bytes(["Regular exercise improves cardiovascular health."])
        sub_docx = _create_docx_bytes(["Regular exercise improves cardiovascular health."])

        response = self.client.post(
            "/analyze",
            files={
                "source_file": ("source.docx", io.BytesIO(source_docx), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
                "submission_file": ("submission.docx", io.BytesIO(sub_docx), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("overall_score", data)
        self.assertIn("overall_risk", data)

    def test_analyze_mixed_pdf_plus_docx(self):
        """Test POST /analyze with PDF source and DOCX submission."""
        source_pdf = _create_minimal_pdf(["Regular exercise improves cardiovascular health."])
        sub_docx = _create_docx_bytes(["Frequent physical activity helps maintain a healthy heart."])

        response = self.client.post(
            "/analyze",
            files={
                "source_file": ("source.pdf", io.BytesIO(source_pdf), "application/pdf"),
                "submission_file": ("submission.docx", io.BytesIO(sub_docx), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("overall_score", data)
        self.assertIn("overall_risk", data)

    def test_analyze_mixed_docx_plus_txt(self):
        """Test POST /analyze with DOCX source and TXT submission."""
        source_docx = _create_docx_bytes(["Regular exercise improves cardiovascular health."])
        sub_txt = b"The university library closes at eight in the evening."

        response = self.client.post(
            "/analyze",
            files={
                "source_file": ("source.docx", io.BytesIO(source_docx), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
                "submission_file": ("submission.txt", io.BytesIO(sub_txt), "text/plain"),
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("overall_score", data)
        self.assertEqual(data["overall_risk"], "LOW")

    def test_analyze_mixed_txt_plus_pdf(self):
        """Test POST /analyze with TXT source and PDF submission."""
        source_txt = b"Regular exercise improves cardiovascular health."
        sub_pdf = _create_minimal_pdf(["Regular exercise improves cardiovascular health."])

        response = self.client.post(
            "/analyze",
            files={
                "source_file": ("source.txt", io.BytesIO(source_txt), "text/plain"),
                "submission_file": ("submission.pdf", io.BytesIO(sub_pdf), "application/pdf"),
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("overall_score", data)

    def test_analyze_unsupported_file_extension(self):
        """Test POST /analyze rejects unsupported extensions with 400 Bad Request."""
        valid_txt = b"Valid text content."
        invalid_img = b"\x89PNG\r\n\x1a\nfakeimage"

        response = self.client.post(
            "/analyze",
            files={
                "source_file": ("source.txt", io.BytesIO(valid_txt), "text/plain"),
                "submission_file": ("image.png", io.BytesIO(invalid_img), "image/png"),
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Unsupported file format", response.json()["detail"])

    def test_analyze_empty_document(self):
        """Test POST /analyze rejects empty or whitespace-only documents with 400."""
        valid_txt = b"Valid text content."
        empty_txt = b"   \n\n  \t "

        # Empty submission
        response = self.client.post(
            "/analyze",
            files={
                "source_file": ("source.txt", io.BytesIO(valid_txt), "text/plain"),
                "submission_file": ("empty.txt", io.BytesIO(empty_txt), "text/plain"),
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("contains no extractable or usable text", response.json()["detail"])

        # Empty source
        response_src = self.client.post(
            "/analyze",
            files={
                "source_file": ("empty.txt", io.BytesIO(empty_txt), "text/plain"),
                "submission_file": ("submission.txt", io.BytesIO(valid_txt), "text/plain"),
            },
        )
        self.assertEqual(response_src.status_code, 400)
        self.assertIn("contains no extractable or usable text", response_src.json()["detail"])

    def test_analyze_missing_upload(self):
        """Test POST /analyze returns 422 when required upload fields are missing."""
        valid_txt = b"Valid text content."

        # Missing submission_file
        response = self.client.post(
            "/analyze",
            files={
                "source_file": ("source.txt", io.BytesIO(valid_txt), "text/plain"),
            },
        )
        self.assertEqual(response.status_code, 422)

        # Missing both files
        response_both = self.client.post("/analyze")
        self.assertEqual(response_both.status_code, 422)


if __name__ == "__main__":
    unittest.main()
