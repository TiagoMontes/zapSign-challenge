from dataclasses import dataclass


@dataclass
class Company:
    id: int | None = None
    name: str = ""
    api_token: str = ""

