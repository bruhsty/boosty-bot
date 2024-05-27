import argparse
import asyncio
import logging
import sys
from datetime import timedelta

from common.adapters.boosty import BoostyAPI
from redis.asyncio import Redis

import config

from .adapters import BoostyProfileStorage
from .service_layer import BoostyProfileUpdater


async def main():
    parser = argparse.ArgumentParser(
        prog="profile_updater",
        description="Fetches subscription levels and subscribers "
        "from boosty and stores them in redis",
    )
    parser.add_argument(
        "-c", "--config", type=str, default="config.yaml", help="path to config file"
    )

    args = parser.parse_args(sys.argv[1:])

    cfg = config.parse_file(args.config)

    logging.basicConfig(
        level=logging.INFO, stream=sys.stdout, format="%(asctime)s %(levelname)s: %(message)s"
    )

    api_client = BoostyAPI(cfg.boosty.access_token, cfg.boosty.refresh_token)

    redis = Redis(
        host=cfg.redis.host,
        port=cfg.redis.port,
        db=cfg.redis.db,
        password=cfg.redis.password,
    )
    profile_storage = BoostyProfileStorage(redis, level_lifetime=timedelta(hours=1))
    updater = BoostyProfileUpdater(
        cfg.boosty.author, api_client, profile_storage, period=timedelta(hours=1)
    )

    await updater.run()


if __name__ == "__main__":
    asyncio.run(main())
