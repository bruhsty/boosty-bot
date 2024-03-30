from typing import Literal

from dependency_injector.wiring import Provide, inject

from app.bot import BruhstyBot
from app.container import AppContainer


@inject
def main(
    updates_type: Literal["polling", "webhook"] = Provide[AppContainer.config.bot.updates],
):
    bot = BruhstyBot()

    if updates_type == "polling":
        bot.start_polling()
    elif updates_type == "webhook":
        bot.start_webhook()
    else:
        raise AssertionError("Invalid updates type")


if __name__ == "__main__":
    container = AppContainer()
    container.config.from_yaml("./config/config.yaml")
    container.init_resources()
    container.wire(
        modules=[
            __name__,
            ".bot",
            "registration.bot.handlers",
            "registration.service_layer.handlers",
        ],
    )
    main()
