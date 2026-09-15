"""PlagiSense FastAPI backend application.

Provides health check, document upload/extraction & NLP analysis endpoint,
API documentation, and CORS configuration for frontend clients.
"""

from pathlib import Path
import tempfile
import shutil

from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

from backend.document_parser import SUPPORTED_EXTENSIONS, extract_text_from_file
from backend.nlp import analyze_documents

app = FastAPI(
    title="PlagiSense API",
    description="Backend API service for PlagiSense plagiarism detection platform.",
    version="1.0.0",
)

# Allowed frontend origins
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Health check endpoint to verify backend service status."""
    return {
        "status": "ok",
        "service": "PlagiSense API",
    }


@app.post("/analyze")
async def analyze_documents_endpoint(
    source_file: UploadFile = File(...),
    submission_file: UploadFile = File(...),
):
    """Document upload, text extraction, and NLP plagiarism analysis endpoint.

    Validates file extensions, extracts text from source and submission documents,
    and runs the explainable NLP evidence engine.
    """
    # 1. Validate file names and extensions
    source_name = source_file.filename or ""
    submission_name = submission_file.filename or ""

    source_ext = Path(source_name).suffix.lower()
    submission_ext = Path(submission_name).suffix.lower()

    supported_str = ", ".join(sorted(SUPPORTED_EXTENSIONS))

    if source_ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{source_ext}' for source file '{source_name}'. Supported formats are: {supported_str}",
        )

    if submission_ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{submission_ext}' for submission file '{submission_name}'. Supported formats are: {supported_str}",
        )

    # 2. Save uploaded files to a temporary directory and extract text
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        source_temp_path = temp_dir_path / f"source_{Path(source_name).name}"
        submission_temp_path = temp_dir_path / f"submission_{Path(submission_name).name}"

        # Write uploaded file contents to temp disk
        with open(source_temp_path, "wb") as f_out:
            shutil.copyfileobj(source_file.file, f_out)

        with open(submission_temp_path, "wb") as f_out:
            shutil.copyfileobj(submission_file.file, f_out)

        # 3. Extract text using document_parser
        try:
            source_text = extract_text_from_file(str(source_temp_path))
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error extracting text from source file '{source_name}': {exc}",
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unexpected error processing source file '{source_name}': {exc}",
            )

        try:
            submission_text = extract_text_from_file(str(submission_temp_path))
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error extracting text from submission file '{submission_name}': {exc}",
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unexpected error processing submission file '{submission_name}': {exc}",
            )

        # 4. Check for empty / no usable text
        if not source_text or not source_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Source file '{source_name}' contains no extractable or usable text.",
            )

        if not submission_text or not submission_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Submission file '{submission_name}' contains no extractable or usable text.",
            )

    # 5. Run NLP engine analysis
    try:
        nlp_result = analyze_documents(source_text, submission_text)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running NLP analysis: {exc}",
        )

    # 6. Expose the real NLP result with summary fields
    overall = nlp_result.get("overall", {})
    matches = nlp_result.get("matches", [])

    return {
        "overall_score": overall.get("risk_score", 0.0),
        "overall_risk": overall.get("risk_level", "LOW"),
        "semantic_similarity": overall.get("semantic_similarity", 0.0),
        "lexical_similarity": overall.get("lexical_similarity", 0.0),
        "concept_overlap": overall.get("concept_overlap", 0.0),
        "suspicious_passages": len(matches),
        "overall": overall,
        "matches": matches,
    }
