"""Signer repository implementation."""

from typing import Optional, List
from django.core.exceptions import ObjectDoesNotExist
from core.domain.entities.signer import Signer
from core.orm.models import Signer as SignerModel
from core.orm.mappers import SignerMapper


class DjangoSignerRepository:
    """Django ORM implementation of SignerRepository."""

    def save(self, signer: Signer) -> Signer:
        """Save a signer and return it with ID."""
        # Map entity to model using the mapper (includes sign_url)
        model_data = SignerMapper.to_model_data(signer)

        if signer.id:
            # Update existing
            SignerModel.objects.filter(id=signer.id).update(**model_data)
            model = SignerModel.objects.get(id=signer.id)
        else:
            # Create new
            model = SignerModel.objects.create(**model_data)

        # Map back to entity
        return SignerMapper.to_entity(model)

    def save_bulk(self, signers: List[Signer]) -> List[Signer]:
        """Save multiple signers and return them with IDs."""
        saved_signers = []
        for signer in signers:
            saved_signer = self.save(signer)
            saved_signers.append(saved_signer)
        return saved_signers

    def find_by_id(self, signer_id: int) -> Optional[Signer]:
        """Find a signer by ID."""
        try:
            model = SignerModel.objects.prefetch_related('documents').get(id=signer_id)
            return SignerMapper.to_entity(model)
        except ObjectDoesNotExist:
            return None

    def find_all(self) -> List[Signer]:
        """Find all signers."""
        models = SignerModel.objects.prefetch_related('documents').all().order_by('-id')
        return [SignerMapper.to_entity(model) for model in models]

    def delete_by_id(self, signer_id: int) -> bool:
        """Delete a signer by ID."""
        deleted_count, _ = SignerModel.objects.filter(id=signer_id).delete()
        return deleted_count > 0