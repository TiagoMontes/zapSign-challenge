from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CreateCompanyDTO:
    name: str
    api_token: str = ""


@dataclass
class CompanyDTO:
    id: int
    name: str
    api_token: str


@dataclass
class CreateSignerDTO:
    name: str
    email: str
    external_id: str = ""


@dataclass
class SignerDTO:
    id: int
    name: str
    email: str
    token: str
    status: str
    external_id: str


@dataclass
class CreateDocumentDTO:
    company_id: int
    name: str
    signer_ids: Optional[List[int]] = None
    external_id: str = ""
    created_by: str = ""


@dataclass
class DocumentResponseDTO:
    id: int
    company_id: int
    name: str
    status: str
    token: str
    open_id: int | None
    external_id: str

