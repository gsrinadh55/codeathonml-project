"""Document parsing layer for PlagiSense.

Supports text extraction from .txt, .pdf, and .docx files with encoding fallback,
whitespace normalization, and corrupted file handling.
"""

from pathlib import Path
import re
from typing import Set

from docx import Document
from pypdf import PdfReader

SUPPORTED_EXTENSIONS: Set[str] = {".txt", ".pdf", ".docx"}


def _normalize_whitespace(text: str) -> str:
    """Normalize whitespace in extracted text while preserving document structure.
    
    - Converts carriage returns to standard newlines.
    - Strips leading and trailing whitespace from individual lines.
    - Collapses excessive blank lines (3+ into 2).
    - Strips overall leading and trailing whitespace.
    """
    if not text:
        return ""
    
    # Standardize line endings
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    
    # Strip whitespace from each line
    lines = [line.strip() for line in normalized.splitlines()]
    
    # Join and collapse multiple consecutive blank lines
    combined = "\n".join(lines)
    combined = re.sub(r"\n{3,}", "\n\n", combined)
    
    return combined.strip()


def _extract_from_txt(path: Path) -> str:
    """Extract text from a .txt file trying standard and fallback encodings."""
    if path.stat().st_size == 0:
        return ""

    encodings = ["utf-8", "utf-8-sig", "cp1252", "latin-1", "iso-8859-1"]
    raw_bytes = path.read_bytes()

    for enc in encodings:
        try:
            return raw_bytes.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue

    # Fallback with replacement if all decode attempts fail
    return raw_bytes.decode("utf-8", errors="replace")


def _extract_from_pdf(path: Path) -> str:
    """Extract text from every page of a .pdf file using pypdf."""
    if path.stat().st_size == 0:
        return ""

    try:
        reader = PdfReader(str(path))
    except Exception as exc:
        raise ValueError(f"Failed to parse corrupted or invalid PDF file: {exc}") from exc

    pages_text = []
    for page in reader.pages:
        try:
            page_text = page.extract_text()
            if page_text:
                pages_text.append(page_text)
        except Exception:
            continue

    return "\n\n".join(pages_text)


def _extract_from_docx(path: Path) -> str:
    """Extract non-empty paragraph text from a .docx file using python-docx."""
    if path.stat().st_size == 0:
        return ""

    try:
        doc = Document(str(path))
    except Exception as exc:
        raise ValueError(f"Failed to parse corrupted or invalid DOCX file: {exc}") from exc

    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()]
    return "\n\n".join(paragraphs)


def extract_text_from_file(file_path: str) -> str:
    """Extract and normalize text content from supported document formats (.txt, .pdf, .docx).

    Args:
        file_path: Path to the document file.

    Returns:
        Extracted and whitespace-normalized text as a string.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file format is unsupported or the file is corrupted.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not path.is_file():
        raise ValueError(f"Path is not a regular file: {file_path}")

    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        supported_str = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValueError(f"Unsupported file format '{ext}'. Supported formats are: {supported_str}")

    if ext == ".txt":
        raw_text = _extract_from_txt(path)
    elif ext == ".pdf":
        raw_text = _extract_from_pdf(path)
    elif ext == ".docx":
        raw_text = _extract_from_docx(path)
    else:
        raise ValueError(f"Unhandled file extension: {ext}")

    return _normalize_whitespace(raw_text)
