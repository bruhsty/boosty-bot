from aiogram.fsm.state import State, StatesGroup


class MenuStatesGroup(StatesGroup):
    main = State()
    email_list = State()
    email_settings = State()
    email_remove_confirmation = State()
    email_add = State()
