from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Company:
    id: Optional[int] = None
    name: str = ""
    api_token: str = ""
    created_at: Optional[datetime] = None
    last_updated_at: Optional[datetime] = None

