from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Company:
    id: int | None = None
    name: str = ""
    api_token: str = ""
    created_at: datetime | None = None
    last_updated_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Company.name must not be empty")

