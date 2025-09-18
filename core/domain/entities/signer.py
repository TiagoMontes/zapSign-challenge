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
    sign_url: str = ""
    company_id: Optional[int] = None
    created_at: Optional[datetime] = None
    last_updated_at: Optional[datetime] = None
    document_ids: List[int] = field(default_factory=list)
    # ZapSign sync fields
    times_viewed: Optional[int] = None
    last_view_at: Optional[datetime] = None
    signed_at: Optional[datetime] = None

