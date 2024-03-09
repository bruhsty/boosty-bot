from typing import Protocol, AsyncIterable

from bruhsty.storage.verification_codes.models import Code, EditableFields
from bruhsty.storage.specs import Specification


class CodeStorage(Protocol):

    async def add(self, telegram_id: int, email: str, code: str) -> Code:
        ...

    async def update(self, code_id: int, **updates: EditableFields) -> Code:
        ...

    async def find(self, spec: Specification) -> AsyncIterable[Code]:
        ...
