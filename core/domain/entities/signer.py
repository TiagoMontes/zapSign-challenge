from dataclasses import dataclass
from datetime import datetime
from typing import Optional


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

