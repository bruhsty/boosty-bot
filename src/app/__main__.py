import argparse
import pathlib
import sys
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


def parse_cli_args():
    parser = argparse.ArgumentParser(prog="bruhsty")
    parser.add_argument(
        "-c",
        "--config",
        type=pathlib.Path,
        default=pathlib.Path("./config/config.yaml"),
        help="path to config file",
    )
    return parser.parse_args(sys.argv[1:])


if __name__ == "__main__":
    container = AppContainer()
    args = parse_cli_args()
    container.config.from_yaml(args.config)

    container.init_resources()
    container.wire(
        modules=[
            __name__,
            ".bot",
            "user.bot.handlers",
            "user.service_layer.handlers",
        ],
    )
    main()
