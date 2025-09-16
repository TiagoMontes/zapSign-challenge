from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


@dataclass
class Document:
    id: Optional[int] = None
    company_id: Optional[int] = None
    name: str = ""
    status: str = ""
    token: str = ""
    open_id: Optional[int] = None
    created_by: str = ""
    external_id: str = ""
    created_at: Optional[datetime] = None
    last_updated_at: Optional[datetime] = None
    signer_ids: List[int] = field(default_factory=list)

    # PDF processing fields
    pdf_url: Optional[str] = None
    processing_status: str = "UPLOADED"  # UPLOADED, PROCESSING, INDEXED, FAILED
    checksum: Optional[str] = None
    version_id: Optional[str] = None

    # Soft delete fields
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by: str = ""

    def __post_init__(self) -> None:
        if not self.company_id:
            raise ValueError("Document.company_id is required")
        if not self.name or not self.name.strip():
            raise ValueError("Document.name must not be empty")

    def can_be_signed(self) -> bool:
        # Simplified rule for M2
        return len(self.signer_ids) > 0 and self.status in ("", "draft", "pending")

    def can_be_analyzed(self) -> bool:
        """Check if document can be analyzed.

        Business rule: Document can be analyzed if:
        - It's active (not soft deleted)
        - Has a name (content to analyze)
        - Has an ID (persisted in database)
        - PDF processing is complete (status = INDEXED)
        """
        return (
            self.is_active() and
            bool(self.name.strip()) and
            self.id is not None and
            self.processing_status == "INDEXED"
        )

    def add_signer(self, signer_id: int) -> None:
        if signer_id not in self.signer_ids:
            self.signer_ids.append(signer_id)

    def is_active(self) -> bool:
        """Check if document is not soft deleted."""
        return not self.is_deleted

    def soft_delete(self, deleted_by: str) -> None:
        """Mark document as soft deleted with audit information."""
        if self.is_deleted:
            raise ValueError("Document is already deleted")
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
        self.deleted_by = deleted_by

    def restore(self) -> None:
        """Restore a soft deleted document."""
        if not self.is_deleted:
            raise ValueError("Document is not deleted")
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = ""

