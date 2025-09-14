from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Company:
    name: str
    api_token: str
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    last_updated_at: Optional[datetime] = None

    def is_valid(self) -> bool:
        """Check if the company entity is valid."""
        errors = self.get_validation_errors()
        return len(errors) == 0

    def get_validation_errors(self) -> dict[str, str]:
        """Get validation errors for the company entity."""
        errors: dict[str, str] = {}

        # Validate name
        if not self.name or self.name.strip() == "":
            errors["name"] = "Company name is required and cannot be empty"
        elif len(self.name) > 255:
            errors["name"] = "Company name cannot be longer than 255 characters"

        # Validate api_token
        if not self.api_token or self.api_token.strip() == "":
            errors["api_token"] = "Company API token is required and cannot be empty"
        elif len(self.api_token) > 255:
            errors["api_token"] = "Company API token cannot be longer than 255 characters"

        return errors

