from abc import ABC, abstractmethod
from typing import Optional


class PDFProcessingError(Exception):
    """Raised when PDF processing fails."""
    pass


class PDFExtractionService(ABC):
    """Abstract interface for PDF text extraction."""

    @abstractmethod
    def download_and_extract_text(self, url: str) -> tuple[str, str]:
        """Download PDF from URL and extract text.

        Args:
            url: URL to download PDF from

        Returns:
            Tuple of (extracted_text, checksum)

        Raises:
            PDFProcessingError: If download or extraction fails
        """
        pass

    @abstractmethod
    def calculate_checksum(self, pdf_bytes: bytes) -> str:
        """Calculate SHA256 checksum of PDF bytes.

        Args:
            pdf_bytes: PDF file bytes

        Returns:
            SHA256 checksum as hex string
        """
        pass

    @abstractmethod
    def validate_pdf_file(self, pdf_bytes: bytes) -> bool:
        """Validate if bytes represent a valid PDF file.

        Args:
            pdf_bytes: File bytes to validate

        Returns:
            True if valid PDF, False otherwise
        """
        pass