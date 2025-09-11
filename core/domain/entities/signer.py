from dataclasses import dataclass


@dataclass
class Signer:
    id: int | None = None
    name: str = ""
    email: str = ""
    token: str = ""
    status: str = ""
    external_id: str = ""

