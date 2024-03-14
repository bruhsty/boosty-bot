import typing
from typing import Any, AsyncIterable, Sequence

from typing_extensions import Unpack

from . import schemas
from ..models import User, UserUpdate
from ...specs import Specification, Field
from ...sql import BaseSQLStorage


class UserStorage(BaseSQLStorage):
    Schema = schemas.User
    ModelGet = User
    ModelCreate = User
    ModelUpdate = UserUpdate

    if typing.TYPE_CHECKING:
        async def create(self, model: User) -> User:
            ...

        def update(
                self,
                filter_: Specification,
                **updates: Unpack[UserUpdate],
        ) -> None:
            ...

        def find(
                self,
                filter_: Specification,
                limit: int | None = None,
                offset: int | None = None,
        ) -> AsyncIterable[User]:
            ...

        async def find_all(
                self,
                filter_: Specification,
                limit: int | None = None,
                offset: int | None = None,
        ) -> Sequence[User]:
            ...

        async def delete(
                self,
                filter_: Specification
        ) -> None:
            ...

    def model_to_schema(self, model: User) -> schemas.User:
        return schemas.User(
            telegram_id=model.telegram_id,
            email=model.email,
            is_verified=model.is_verified,
        )

    def schema_to_model(self, schema: schemas.User) -> User:
        return schema.to_model()

    def resolve_name(self, name: str) -> Any:
        assert isinstance(User.telegram_id, Field)
        return {
            User.telegram_id.field: schemas.User.telegram_id,
            User.email.field: schemas.User.email,
            User.is_verified.field: schemas.User.is_verified,
        }[name]
