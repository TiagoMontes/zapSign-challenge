from __future__ import annotations

from typing import Iterable, Optional

from core.domain.entities.signer import Signer as SignerEntity
from core.orm.models import Signer as SignerModel
from core.orm.mappers import (
    signer_model_to_entity,
    signer_entity_to_model_data,
    map_signers,
)


class SignerRepository:
    def create(self, signer: SignerEntity) -> SignerEntity:
        obj = SignerModel.objects.create(**signer_entity_to_model_data(signer))
        return signer_model_to_entity(obj)

    def get_by_id(self, signer_id: int) -> Optional[SignerEntity]:
        obj = SignerModel.objects.filter(id=signer_id).first()
        return signer_model_to_entity(obj) if obj else None

    def list(self) -> Iterable[SignerEntity]:
        return map_signers(SignerModel.objects.order_by("-id").all())

    def delete(self, signer_id: int) -> None:
        SignerModel.objects.filter(id=signer_id).delete()

