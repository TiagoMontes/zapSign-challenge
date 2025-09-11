from __future__ import annotations

from typing import Iterable, Optional

from core.domain.entities.signer import Signer


class InMemorySignerRepository:
    def __init__(self) -> None:
        self._seq = 0
        self._items: dict[int, Signer] = {}

    def create(self, signer: Signer) -> Signer:
        self._seq += 1
        s = Signer(
            id=self._seq,
            name=signer.name,
            email=signer.email,
            token=signer.token,
            status=signer.status,
            external_id=signer.external_id,
        )
        self._items[self._seq] = s
        return s

    def get_by_id(self, signer_id: int) -> Optional[Signer]:
        return self._items.get(signer_id)

    def list(self) -> Iterable[Signer]:
        return list(self._items.values())

    def delete(self, signer_id: int) -> None:
        self._items.pop(signer_id, None)

