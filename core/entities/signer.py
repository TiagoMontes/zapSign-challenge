from dataclasses import dataclass


@dataclass
class Signer:
    id: int | None = None
    name: str = ""
    email: str = ""
    token: str = ""
    status: str = ""
    external_id: str = ""

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Signer.name must not be empty")
        if "@" not in self.email:
            raise ValueError("Signer.email must be a valid email")

