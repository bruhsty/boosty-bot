from aiogram.types import Message


async def start_command(msg: Message):
    await msg.answer("Привет!")
