import logging

from bruhsty import config
from bruhsty.bot import BruhstyBot
from bruhsty.config import UpdateType


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
