import hashlib
import io
from typing import Optional
import requests
from pypdf import PdfReader  # type: ignore[import-untyped]

from .interfaces import PDFExtractionService, PDFProcessingError


class PDFService(PDFExtractionService):
    """Concrete implementation of PDF processing service."""

    def __init__(
        self,
        timeout: int = 30,
        max_file_size: int = 50 * 1024 * 1024,  # 50MB
    ):
        """Initialize PDF service.

        Args:
            timeout: HTTP request timeout in seconds
            max_file_size: Maximum file size in bytes
        """
        self.timeout = timeout
        self.max_file_size = max_file_size

    def download_and_extract_text(self, url: str) -> tuple[str, str]:
        """Download PDF from URL and extract text.

        Args:
            url: URL to download PDF from

        Returns:
            Tuple of (extracted_text, checksum)

        Raises:
            PDFProcessingError: If download or extraction fails
        """
        try:
            # Download PDF with size limit
            pdf_bytes = self._download_pdf(url)

            # Validate PDF file
            if not self.validate_pdf_file(pdf_bytes):
                raise PDFProcessingError(f"Invalid PDF file from URL: {url}")

            # Calculate checksum
            checksum = self.calculate_checksum(pdf_bytes)

            # Extract text
            text = self._extract_text_from_bytes(pdf_bytes)

            return text, checksum

        except requests.RequestException as e:
            raise PDFProcessingError(f"Failed to download PDF from {url}: {str(e)}")
        except Exception as e:
            raise PDFProcessingError(f"PDF processing failed for {url}: {str(e)}")

    def _download_pdf(self, url: str) -> bytes:
        """Download PDF file from URL with validations.

        Args:
            url: URL to download from

        Returns:
            PDF file bytes

        Raises:
            PDFProcessingError: If download fails or file is too large
        """
        response = requests.get(
            url,
            timeout=self.timeout,
            stream=True,
            headers={
                'User-Agent': 'ZapSign-PDF-Processor/1.0'
            }
        )
        response.raise_for_status()

        # Check content type if provided
        content_type = response.headers.get('content-type', '').lower()
        if content_type and 'pdf' not in content_type:
            print(f"Warning: Content-Type is '{content_type}', expected PDF")

        # Download with size limit
        content = b''
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                content += chunk
                if len(content) > self.max_file_size:
                    raise PDFProcessingError(
                        f"File too large: {len(content)} bytes > {self.max_file_size} bytes"
                    )

        if not content:
            raise PDFProcessingError("Downloaded file is empty")

        return content

    def _extract_text_from_bytes(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF bytes using pypdf.

        Args:
            pdf_bytes: PDF file bytes

        Returns:
            Extracted text content

        Raises:
            PDFProcessingError: If text extraction fails
        """
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            reader = PdfReader(pdf_file)

            if len(reader.pages) == 0:
                raise PDFProcessingError("PDF contains no pages")

            text_parts = []
            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_parts.append(f"=== Página {page_num + 1} ===\n{page_text}\n")
                except Exception as e:
                    print(f"Warning: Failed to extract text from page {page_num + 1}: {e}")
                    continue

            if not text_parts:
                raise PDFProcessingError("No text could be extracted from PDF")

            return "\n".join(text_parts)

        except Exception as e:
            if isinstance(e, PDFProcessingError):
                raise
            raise PDFProcessingError(f"Text extraction failed: {str(e)}")

    def calculate_checksum(self, pdf_bytes: bytes) -> str:
        """Calculate SHA256 checksum of PDF bytes.

        Args:
            pdf_bytes: PDF file bytes

        Returns:
            SHA256 checksum as hex string
        """
        return hashlib.sha256(pdf_bytes).hexdigest()

    def validate_pdf_file(self, pdf_bytes: bytes) -> bool:
        """Validate if bytes represent a valid PDF file.

        Args:
            pdf_bytes: File bytes to validate

        Returns:
            True if valid PDF, False otherwise
        """
        if len(pdf_bytes) < 4:
            return False

        # Check PDF magic number
        if not pdf_bytes.startswith(b'%PDF'):
            return False

        # Try to create PdfReader to validate structure
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            reader = PdfReader(pdf_file)
            # Just check if we can access pages without error
            _ = len(reader.pages)
            return True
        except Exception:
            return False