from common.adapters.sql import SQLStorage
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from user.domain import models

from . import schema


class UserStorage(SQLStorage[int]):
    db_model = schema.User
    load_options = [joinedload(schema.User.emails).joinedload(schema.UserEmail.verification_codes)]

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def close(self) -> None:
        pass

    def _to_domain(self, db_model: schema.User) -> models.User:
        return schema.User.to_model(db_model)

    def _to_db_model(self, item: models.User) -> schema.User:
        return schema.User.from_model(item)
