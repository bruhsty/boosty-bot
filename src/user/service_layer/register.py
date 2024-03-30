import os
import struct

from ..domain.models import User
from .unit_of_work import UnitOfWork


class UserNotFoundError(Exception):
    pass


def get_random_code() -> str:
    raw_bytes = os.urandom(6)
    raw_code = struct.unpack("!i", raw_bytes)
    str_code = f"{raw_code:06d}"
    return f"{str_code[:3]}-{str_code[3:]}"


async def get_or_create_user(
    telegram_id: int,
    uow: UnitOfWork,
) -> User:
    async with uow:
        user = await uow.user_storage.get(telegram_id)
        if user is None:
            user = User(telegram_id)
            await uow.user_storage.add(user)
            await uow.commit()
        return user


async def add_email(
    telegram_id: int,
    new_email: str,
    uow: UnitOfWork,
) -> None:
    async with uow:
        user = await uow.user_storage.get(telegram_id)
        user.add_email(new_email)
        await uow.user_storage.persist(user)
        await uow.commit()


async def remove_email(
    telegram_id: int,
    email: str,
    uow: UnitOfWork,
) -> None:
    async with uow:
        user = await uow.user_storage.get(telegram_id)
        user.remove_email(email)
        await uow.user_storage.persist(user)
        await uow.commit()


async def confirm_email(
    telegram_id: int,
    email: str,
    code: str,
    uow: UnitOfWork,
) -> None:
    async with uow:
        user = await uow.user_storage.get(telegram_id)
        user.verify_email(email, code)
        await uow.user_storage.persist(user)
        await uow.commit()


async def resend_code(
    telegram_id: int,
    email: str,
    uow: UnitOfWork,
) -> None:
    async with uow:
        user = await uow.user_storage.get(telegram_id)
        user.issue_verification_code(email, User.CODE_GENERATOR())
        await uow.user_storage.persist(user)
        await uow.commit()
