from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class Document:
    id: int | None = None
    company_id: int | None = None
    name: str = ""
    status: str = ""
    token: str = ""
    open_id: int | None = None
    created_by: str = ""
    external_id: str = ""
    created_at: datetime | None = None
    last_updated_at: datetime | None = None
    signer_ids: List[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.company_id:
            raise ValueError("Document.company_id is required")
        if not self.name or not self.name.strip():
            raise ValueError("Document.name must not be empty")

    def can_be_signed(self) -> bool:
        # Simplified rule for M2
        return len(self.signer_ids) > 0 and self.status in ("", "draft", "pending")

    def add_signer(self, signer_id: int) -> None:
        if signer_id not in self.signer_ids:
            self.signer_ids.append(signer_id)

