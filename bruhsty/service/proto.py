from typing import Protocol, Sequence
from typing_extensions import Unpack
from bruhsty.storage.verification_codes.models import Code, CodeEdit, CodeCreate
from bruhsty.storage.specs import Specification


class CodeStorage(Protocol):

    async def create(self, model: CodeCreate) -> Code:
        ...

    async def update(self, code_id: int, **updates: Unpack[CodeEdit]) -> Code:
        ...

    def find_all(
            self,
            spec: Specification,
            limit: int | None = None,
            offset: int | None = None
    ) -> Sequence[Code]:
        ...
