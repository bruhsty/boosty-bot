import re

from aiogram import F
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Column, Row, Select
from aiogram_dialog.widgets.text import Const, Format

from .handlers import (
    add_email,
    email_resend_code,
    email_validate,
    get_email_list,
    go_back,
    list_emails,
    on_email_selected,
    on_input_verification_code,
    remove_email,
    switch_window,
    test_getter,
)
from .state import MenuStatesGroup

go_back_button = Button(Const("Назад"), id="menu.back", on_click=go_back)

menu_dialog = Dialog(
    Window(
        Const("Меню: "),
        Row(
            Button(Const("Добавить email"), id="menu.add_email", on_click=add_email),
            Button(Const("Мои имейлы"), id="menu.list_emails", on_click=list_emails),
        ),
        state=MenuStatesGroup.main,
    ),
    Window(
        Const("Ваши имейлы:"),
        Column(
            Select(
                Format("{item[email]}"),
                id="menu.email_list",
                items="emails",
                item_id_getter=lambda email: email["email"],
                on_click=on_email_selected,
            ),
            go_back_button,
        ),
        state=MenuStatesGroup.email_list,
        getter=get_email_list,
    ),
    Window(
        Format("{selected_email[email]}"),
        Button(
            Const("Подтвердить"),
            id="menu.email.verify",
            when=F["dialog_data"]["selected_email"]["is_verified"].__invert__(),  # type: ignore
            on_click=email_resend_code,
        ),
        Button(Const("Отвязать"), id="menu.email.remove", on_click=remove_email),
        go_back_button,
        state=MenuStatesGroup.email_settings,
        getter=get_email_list,
    ),
    Window(
        Const("Введите новый email"),
        TextInput(
            id="menu.add_email.email_input",
            filter=lambda msg: re.fullmatch(
                r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", msg.text
            ),
            on_error=switch_window(MenuStatesGroup.invalid_email_value),
            on_success=email_validate,
        ),
        go_back_button,
        getter=test_getter,
        state=MenuStatesGroup.email_add,
    ),
    Window(
        Const("На ваш email отправили код, введите его, чтобы завершить регистрацию"),
        TextInput(
            id="menu.add_email.code_input",
            filter=lambda msg: msg.text.isnumeric() and len(msg.text) == 4,
            on_error=switch_window(MenuStatesGroup.invalid_email_value),
            on_success=on_input_verification_code,
        ),
        getter=test_getter,
        state=MenuStatesGroup.email_verify,
    ),
    Window(
        Const("Вы ввели некорректный email. Попробуйте ещё раз:"),
        go_back_button,
        getter=test_getter,
        state=MenuStatesGroup.invalid_email_value,
    ),
    Window(
        Const("Вы ввели неверный код. попробуйте ещё раз."),
        go_back_button,
        getter=test_getter,
        state=MenuStatesGroup.invalid_code,
    ),
    Window(
        Const("Вы добавили новый email!"),
        Button(
            id="menu.email_added.go_to_main_menu",
            text=Const("Вернуться в меню"),
            on_click=switch_window(MenuStatesGroup.main),
        ),
        state=MenuStatesGroup.email_successfully_added,
    ),
)
