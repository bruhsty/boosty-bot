import argparse
import logging
import pathlib
import sys

from bruhsty import app
from bruhsty import config


def main():
    parser = argparse.ArgumentParser(prog="bruhsty")
    parser.add_argument("-c", "--config",
                        type=pathlib.Path,
                        default=pathlib.Path("./config/config.yaml"),
                        help="path to config file")
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

    app.run(cfg, logger)


if __name__ == '__main__':
    main()
