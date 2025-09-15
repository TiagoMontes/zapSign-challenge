from dataclasses import dataclass, field, asdict
from typing import List, Optional, Any, Dict, TypedDict
from datetime import datetime


@dataclass
class ZapSignSignerRequest:
    """Value object for ZapSign signer request data."""

    name: str
    email: str = ""
    auth_mode: str = "assinaturaTela"
    send_automatic_email: bool = False
    send_automatic_whatsapp: bool = False
    order_group: Optional[int] = None
    custom_message: str = ""
    phone_country: str = ""
    phone_number: str = ""
    lock_email: bool = False
    blank_email: bool = False
    hide_email: bool = False
    lock_phone: bool = False
    blank_phone: bool = False
    hide_phone: bool = False
    lock_name: bool = False
    require_cpf: bool = False
    cpf: str = ""
    require_selfie_photo: bool = False
    require_document_photo: bool = False
    selfie_validation_type: str = "none"
    selfie_photo_url: str = ""
    document_photo_url: str = ""
    document_verse_photo_url: str = ""
    qualification: str = ""
    external_id: str = ""
    redirect_link: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request."""
        data = asdict(self)
        # Remove None values for cleaner API requests
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class ZapSignDocumentRequest:
    """Value object for ZapSign document creation request."""

    name: str
    url_pdf: str
    signers: List[ZapSignSignerRequest]
    external_id: Optional[str] = None
    lang: str = "pt-br"
    disable_signer_emails: bool = False
    brand_logo: str = ""
    brand_primary_color: str = ""
    brand_name: str = ""
    folder_path: str = "/"
    created_by: str = ""
    date_limit_to_sign: Optional[datetime] = None
    signature_order_active: bool = False
    observers: List[str] = field(default_factory=list)
    reminder_every_n_days: int = 0
    allow_refuse_signature: bool = False
    disable_signers_get_original_file: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request."""
        data = asdict(self)

        # Convert signers to dict
        data["signers"] = [signer.to_dict() for signer in self.signers]

        # Convert datetime to ISO format if present
        if self.date_limit_to_sign:
            data["date_limit_to_sign"] = self.date_limit_to_sign.isoformat()

        # Remove None values
        return {k: v for k, v in data.items() if v is not None}