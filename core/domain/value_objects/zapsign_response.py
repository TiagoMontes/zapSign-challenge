from dataclasses import dataclass
from typing import List, Optional, Dict, Any, TypedDict


class ZapSignSignerAPIData(TypedDict, total=False):
    """TypedDict for ZapSign signer API response data."""
    token: str
    name: str
    status: str
    email: str
    external_id: str
    sign_url: str
    lock_name: bool
    lock_email: bool
    hide_email: bool
    blank_email: bool
    phone_country: str
    phone_number: str
    lock_phone: bool
    hide_phone: bool
    blank_phone: bool
    times_viewed: int
    last_view_at: Optional[str]
    signed_at: Optional[str]
    auth_mode: str
    qualification: str
    require_selfie_photo: bool
    require_document_photo: bool
    geo_latitude: Optional[float]
    geo_longitude: Optional[float]
    redirect_link: str
    signature_image: Optional[str]
    visto_image: Optional[str]
    document_photo_url: str
    document_verse_photo_url: str
    selfie_photo_url: str
    selfie_photo_url2: str
    send_via: str
    resend_attempts: Optional[int]
    cpf: str
    cnpj: str
    send_automatic_whatsapp_signed_file: Optional[bool]
    liveness_photo_url: str
    selfie_validation_type: str
    ip: Optional[str]
    delegator: Optional[str]
    signature_anchor_text: Optional[str]
    rubrica_anchor_text: Optional[str]


class ZapSignDocumentAPIData(TypedDict, total=False):
    """TypedDict for ZapSign document API response data."""
    token: str
    name: str
    status: str
    open_id: int
    external_id: str
    created_by: Dict[str, Any]
    sandbox: bool
    folder_path: str
    folder_token: Optional[str]
    rejected_reason: Optional[str]
    lang: str
    original_file: str
    signed_file: Optional[str]
    extra_docs: List[Dict[str, Any]]
    created_through: str
    deleted: bool
    deleted_at: Optional[str]
    signed_file_only_finished: bool
    disable_signer_emails: bool
    brand_logo: str
    brand_primary_color: str
    created_at: str
    last_update_at: str
    template: Optional[str]
    signers: List[ZapSignSignerAPIData]
    answers: List[Dict[str, Any]]
    auto_reminder: int
    signature_report: Optional[str]
    tsa_country: Optional[str]
    use_timestamp: bool
    metadata: List[Dict[str, Any]]


@dataclass
class ZapSignSignerResponse:
    """Value object for ZapSign signer response data."""

    token: str
    name: str
    status: str
    email: str = ""
    external_id: str = ""
    sign_url: str = ""
    lock_name: bool = False
    lock_email: bool = False
    hide_email: bool = False
    blank_email: bool = False
    phone_country: str = ""
    phone_number: str = ""
    lock_phone: bool = False
    hide_phone: bool = False
    blank_phone: bool = False
    times_viewed: int = 0
    last_view_at: Optional[str] = None
    signed_at: Optional[str] = None
    auth_mode: str = "assinaturaTela"
    qualification: str = ""
    require_selfie_photo: bool = False
    require_document_photo: bool = False
    geo_latitude: Optional[float] = None
    geo_longitude: Optional[float] = None
    redirect_link: str = ""
    signature_image: Optional[str] = None
    visto_image: Optional[str] = None
    document_photo_url: str = ""
    document_verse_photo_url: str = ""
    selfie_photo_url: str = ""
    selfie_photo_url2: str = ""
    send_via: str = ""
    resend_attempts: Optional[int] = None
    cpf: str = ""
    cnpj: str = ""
    send_automatic_whatsapp_signed_file: Optional[bool] = None
    liveness_photo_url: str = ""
    selfie_validation_type: str = "none"
    ip: Optional[str] = None
    delegator: Optional[str] = None
    signature_anchor_text: Optional[str] = None
    rubrica_anchor_text: Optional[str] = None

    @classmethod
    def from_api_data(cls, data: Dict[str, Any]) -> "ZapSignSignerResponse":
        """Create from API response data."""
        return cls(
            token=data.get("token", ""),
            name=data.get("name", ""),
            status=data.get("status", ""),
            email=data.get("email", ""),
            external_id=data.get("external_id", ""),
            sign_url=data.get("sign_url", ""),
            lock_name=data.get("lock_name", False),
            lock_email=data.get("lock_email", False),
            hide_email=data.get("hide_email", False),
            blank_email=data.get("blank_email", False),
            phone_country=data.get("phone_country", ""),
            phone_number=data.get("phone_number", ""),
            lock_phone=data.get("lock_phone", False),
            hide_phone=data.get("hide_phone", False),
            blank_phone=data.get("blank_phone", False),
            times_viewed=data.get("times_viewed", 0),
            last_view_at=data.get("last_view_at"),
            signed_at=data.get("signed_at"),
            auth_mode=data.get("auth_mode", "assinaturaTela"),
            qualification=data.get("qualification", ""),
            require_selfie_photo=data.get("require_selfie_photo", False),
            require_document_photo=data.get("require_document_photo", False),
            geo_latitude=data.get("geo_latitude"),
            geo_longitude=data.get("geo_longitude"),
            redirect_link=data.get("redirect_link", ""),
            signature_image=data.get("signature_image"),
            visto_image=data.get("visto_image"),
            document_photo_url=data.get("document_photo_url", ""),
            document_verse_photo_url=data.get("document_verse_photo_url", ""),
            selfie_photo_url=data.get("selfie_photo_url", ""),
            selfie_photo_url2=data.get("selfie_photo_url2", ""),
            send_via=data.get("send_via", ""),
            resend_attempts=data.get("resend_attempts"),
            cpf=data.get("cpf", ""),
            cnpj=data.get("cnpj", ""),
            send_automatic_whatsapp_signed_file=data.get(
                "send_automatic_whatsapp_signed_file"
            ),
            liveness_photo_url=data.get("liveness_photo_url", ""),
            selfie_validation_type=data.get("selfie_validation_type", "none"),
            ip=data.get("ip"),
            delegator=data.get("delegator"),
            signature_anchor_text=data.get("signature_anchor_text"),
            rubrica_anchor_text=data.get("rubrica_anchor_text"),
        )


@dataclass
class ZapSignDocumentResponse:
    """Value object for ZapSign document response data."""

    token: str
    name: str
    status: str
    open_id: int
    external_id: str = ""
    created_by_email: str = ""
    sandbox: bool = False
    folder_path: str = "/"
    folder_token: Optional[str] = None
    rejected_reason: Optional[str] = None
    lang: str = "pt-br"
    original_file: str = ""
    signed_file: Optional[str] = None
    extra_docs: List[Dict[str, Any]] = None  # type: ignore
    created_through: str = "api"
    deleted: bool = False
    deleted_at: Optional[str] = None
    signed_file_only_finished: bool = False
    disable_signer_emails: bool = False
    brand_logo: str = ""
    brand_primary_color: str = ""
    created_at: str = ""
    last_update_at: str = ""
    template: Optional[str] = None
    signers: List[ZapSignSignerResponse] = None  # type: ignore
    answers: List[Dict[str, Any]] = None  # type: ignore
    auto_reminder: int = 0
    signature_report: Optional[str] = None
    tsa_country: Optional[str] = None
    use_timestamp: bool = True
    metadata: List[Dict[str, Any]] = None  # type: ignore

    def __post_init__(self):
        """Initialize mutable default values."""
        if self.signers is None:
            self.signers = []
        if self.extra_docs is None:
            self.extra_docs = []
        if self.answers is None:
            self.answers = []
        if self.metadata is None:
            self.metadata = []

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "ZapSignDocumentResponse":
        """Create from API response data."""
        # Parse signers
        signers = [
            ZapSignSignerResponse.from_api_data(signer_data)
            for signer_data in data.get("signers", [])
        ]

        # Extract created_by email
        created_by_email = ""
        if created_by := data.get("created_by"):
            if isinstance(created_by, dict):
                created_by_email = created_by.get("email", "")

        return cls(
            token=data.get("token", ""),
            name=data.get("name", ""),
            status=data.get("status", ""),
            open_id=data.get("open_id", 0),
            external_id=data.get("external_id") or "",
            created_by_email=created_by_email,
            sandbox=data.get("sandbox", False),
            folder_path=data.get("folder_path", "/"),
            folder_token=data.get("folder_token"),
            rejected_reason=data.get("rejected_reason"),
            lang=data.get("lang", "pt-br"),
            original_file=data.get("original_file", ""),
            signed_file=data.get("signed_file"),
            extra_docs=data.get("extra_docs", []),
            created_through=data.get("created_through", "api"),
            deleted=data.get("deleted", False),
            deleted_at=data.get("deleted_at"),
            signed_file_only_finished=data.get("signed_file_only_finished", False),
            disable_signer_emails=data.get("disable_signer_emails", False),
            brand_logo=data.get("brand_logo", ""),
            brand_primary_color=data.get("brand_primary_color", ""),
            created_at=data.get("created_at", ""),
            last_update_at=data.get("last_update_at", ""),
            template=data.get("template"),
            signers=signers,
            answers=data.get("answers", []),
            auto_reminder=data.get("auto_reminder", 0),
            signature_report=data.get("signature_report"),
            tsa_country=data.get("tsa_country"),
            use_timestamp=data.get("use_timestamp", True),
            metadata=data.get("metadata", []),
        )