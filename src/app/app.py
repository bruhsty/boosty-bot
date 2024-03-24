import argparse
import logging
import pathlib
import sys

from src import config
from src.bot import BruhstyBot
from src.config import UpdateType


def run(cfg: config.Config, logger: logging.Logger) -> None:
    bot = BruhstyBot(cfg.bot.token, logger)

    if cfg.bot.updates == UpdateType.POLLING:
        assert cfg.bot.polling is not None
        bot.start_polling(cfg.bot.polling.timeout)
    elif cfg.bot.updates == UpdateType.WEBHOOK:
        assert cfg.bot.webhook is not None
        bot.start_webhook(
            host=cfg.bot.webhook.host,
        )
    else:
        raise AssertionError("Unknown update fetching type")


def main() -> None:
    parser = argparse.ArgumentParser(prog="bruhsty")
    parser.add_argument(
        "-c",
        "--config",
        type=pathlib.Path,
        default=pathlib.Path("./config/config.yaml"),
        help="path to config file",
    )
    args = parser.parse_args(sys.argv[1:])

    cfg = config.parse_file(args.config)
    match cfg.env:
        case config.Env.PROD:
            level = logging.INFO
        case config.Env.DEV:
            level = logging.DEBUG
        case _:
            raise AssertionError("environment has invalid value")

    logging.basicConfig(level=level)
    logger = logging.getLogger()
    logger.info(f"logging level {level}", {"level": level})

    run(cfg, logger)


if __name__ == "__main__":
    main()
