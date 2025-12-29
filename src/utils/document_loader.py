"""Document loading utilities for various file formats."""

import os
import base64
import io
from typing import Optional, Tuple
from pathlib import Path
from loguru import logger
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from docx import Document
except ImportError:
    Document = None

try:
    import PyPDF2
    import pdfplumber
except ImportError:
    PyPDF2 = None
    pdfplumber = None

try:
    import fitz  # PyMuPDF
    from PIL import Image
except ImportError:
    fitz = None
    Image = None


class DocumentLoader:
    """Load and extract text from various document formats."""

    @staticmethod
    def load_document(file_path: str) -> Tuple[str, dict]:
        """
        Load a document and extract its text content.

        Args:
            file_path: Path to the document file

        Returns:
            Tuple of (text_content, metadata)

        Raises:
            ValueError: If file format is not supported
            FileNotFoundError: If file does not exist
        """
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        extension = file_path_obj.suffix.lower()

        if extension == ".docx":
            return DocumentLoader._load_docx(file_path)
        elif extension == ".pdf":
            return DocumentLoader._load_pdf(file_path)
        else:
            raise ValueError(f"Unsupported file format: {extension}")

    @staticmethod
    def _load_docx(file_path: str) -> Tuple[str, dict]:
        """Load a DOCX file."""
        if Document is None:
            raise ImportError("python-docx is not installed. Install it with: pip install python-docx")

        logger.info(f"Loading DOCX file: {file_path}")
        doc = Document(file_path)

        paragraphs = []
        for i, para in enumerate(doc.paragraphs):
            if para.text.strip():
                paragraphs.append({
                    "index": i,
                    "text": para.text,
                    "style": para.style.name if para.style else None
                })

        text_content = "\n".join([p["text"] for p in paragraphs])

        metadata = {
            "file_path": file_path,
            "format": "docx",
            "paragraph_count": len(paragraphs),
            "character_count": len(text_content)
        }

        logger.info(f"Loaded {len(paragraphs)} paragraphs from DOCX")
        return text_content, metadata

    @staticmethod
    def _load_pdf(file_path: str) -> Tuple[str, dict]:
        """Load a PDF file with automatic fallback to OCR for image-based PDFs."""
        if pdfplumber is None:
            raise ImportError("pdfplumber is not installed. Install it with: pip install pdfplumber")

        logger.info(f"Loading PDF file: {file_path}")

        text_content = []
        page_count = 0

        # First, try regular text extraction
        with pdfplumber.open(file_path) as pdf:
            page_count = len(pdf.pages)
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    text_content.append(text)

        full_text = "\n".join(text_content)

        # Check if we got meaningful text (more than 100 characters)
        # If not, the PDF is likely image-based and needs OCR
        if len(full_text.strip()) < 100:
            logger.warning("PDF appears to be image-based (no text layer detected)")
            logger.info("Attempting OCR extraction...")
            return DocumentLoader._load_pdf_with_ocr(file_path, page_count)

        metadata = {
            "file_path": file_path,
            "format": "pdf",
            "extraction_method": "text_layer",
            "page_count": page_count,
            "character_count": len(full_text)
        }

        logger.info(f"Loaded {page_count} pages from PDF (text layer)")
        return full_text, metadata

    @staticmethod
    def _load_pdf_with_ocr(file_path: str, page_count: int = None) -> Tuple[str, dict]:
        """
        Load an image-based PDF using OpenAI Vision API with PyMuPDF.

        Args:
            file_path: Path to PDF file
            page_count: Number of pages (if already known)

        Returns:
            Tuple of (text_content, metadata)
        """
        if fitz is None:
            raise ImportError(
                "PyMuPDF is not installed. Install with: pip install PyMuPDF"
            )

        # Check for OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your_openai_api_key_here":
            raise ValueError(
                "OpenAI API key not configured. Please set OPENAI_API_KEY in .env file.\n"
                "OCR for image-based PDFs requires OpenAI Vision API."
            )

        logger.info(f"Starting OCR extraction using OpenAI Vision API for: {file_path}")

        try:
            # Initialize OpenAI client
            client = OpenAI(api_key=api_key)

            # Open PDF with PyMuPDF
            logger.info("Opening PDF and converting pages to images...")
            pdf_document = fitz.open(file_path)

            if page_count is None:
                page_count = len(pdf_document)

            text_content = []

            # Extract text from each page using OpenAI Vision API
            for page_num in range(page_count):
                logger.info(f"Processing page {page_num + 1}/{page_count} with OpenAI Vision API...")

                # Get the page
                page = pdf_document[page_num]

                # Render page to image (pixmap)
                # Use higher DPI for better quality: 300 DPI
                zoom = 300 / 72  # 72 is the default DPI
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)

                # Convert pixmap to PNG bytes
                img_bytes = pix.tobytes("png")

                # Convert to base64
                img_base64 = base64.b64encode(img_bytes).decode('utf-8')

                # Call OpenAI Vision API
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",  # GPT-4 Vision model
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "Extract all text from this image. Maintain the original structure, formatting, and line breaks. Return only the extracted text without any additional commentary."
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/png;base64,{img_base64}"
                                        }
                                    }
                                ]
                            }
                        ],
                        max_tokens=4096
                    )

                    page_text = response.choices[0].message.content

                    if page_text and page_text.strip():
                        text_content.append(page_text.strip())
                        logger.debug(f"Extracted {len(page_text)} characters from page {page_num}")

                except Exception as e:
                    logger.error(f"Failed to process page {page_num}: {e}")
                    # Continue with other pages even if one fails
                    continue

            full_text = "\n\n".join(text_content)

            # Close the PDF document
            pdf_document.close()

            metadata = {
                "file_path": file_path,
                "format": "pdf",
                "extraction_method": "openai_vision_pymupdf",
                "page_count": page_count,
                "character_count": len(full_text),
                "ocr_engine": "gpt-4o"
            }

            logger.info(f"OCR extraction complete: {page_count} pages processed")
            logger.info(f"Extracted {len(full_text)} characters")

            return full_text, metadata

        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            raise RuntimeError(
                f"Failed to extract text from image-based PDF using OpenAI Vision API: {e}\n\n"
                "Troubleshooting:\n"
                "1. Ensure PyMuPDF is installed: pip install PyMuPDF\n"
                "2. Verify OpenAI API key is set in .env file\n"
                "3. Make sure your OpenAI account has access to gpt-4o (Vision model)\n"
                "4. Check PDF file is not corrupted\n"
            )

    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """Validate if file exists and has supported extension."""
        path = Path(file_path)
        if not path.exists():
            return False
        return path.suffix.lower() in [".docx", ".pdf"]
