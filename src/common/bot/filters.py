import aiogram
from app.container import AppContainer
from dependency_injector.wiring import Provide, inject

from config import Admin


@inject
async def is_admin(
    update: aiogram.types.Update, admins: list[Admin] = Provide[AppContainer.config.admins]
) -> bool:
    if update.callback_query is not None:
        id = update.callback_query.from_user.id
    elif update.message is not None:
        id = update.message.from_user.id
    else:
        return False
    for admin in admins:
        if admin.id == id:
            return True
    else:
        return False
