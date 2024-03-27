from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Column, Row, Select
from aiogram_dialog.widgets.text import Const, Format

from .handlers import (
    add_email,
    cancel_email_input,
    go_back,
    list_emails,
    on_email_selected,
    remove_email,
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
        getter=test_getter,
    ),
    Window(
        Format("{selected_email}"),
        Button(Const("Отвязать"), id="menu.email.remove", on_click=remove_email),
        state=MenuStatesGroup.email_settings,
        getter=test_getter,
    ),
    Window(
        Const("Введите новый email"),
        TextInput(id="menu.add_email.email_input"),
        Button(
            Const("Отменить"), id="menu.add_email.email_input_cancel", on_click=cancel_email_input
        ),
        getter=test_getter,
        state=MenuStatesGroup.email_add,
    ),
)
