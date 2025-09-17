from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class Signer:
    id: Optional[int] = None
    name: str = ""
    email: str = ""
    token: str = ""
    status: str = ""
    external_id: str = ""
    created_at: Optional[datetime] = None
    last_updated_at: Optional[datetime] = None
    document_ids: List[int] = field(default_factory=list)

