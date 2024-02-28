import enum
import pathlib
from typing import Literal

import yaml
from pydantic import field_validator

from pydantic_settings import BaseSettings

__all__ = ["Config", "parse_file", "UpdateType", "Env"]


class Env(str, enum.Enum):
    PROD = "prod"
    DEV = "prod"


class UpdateType(str, enum.Enum):
    WEBHOOK = "webhook"
    POLLING = "polling"


class WebhookConfig(BaseSettings):
    url: str
    host: str
    port: int
    path: str = "/webhook"
    workers: int = 40
    secret_token: str | None = None
    max_connections: int = 40


class PollingConfig(BaseSettings):
    timeout: int = 1


class BotConfig(BaseSettings):
    token: str
    updates: UpdateType
    webhook: WebhookConfig | None
    polling: PollingConfig | None


class BoostyConfig(BaseSettings):
    access_token: str
    refresh_token: str


class SmtpConfig(BaseSettings):
    host: str
    port: int
    username: str
    password: str
    use_tls: bool = True


class Config(BaseSettings):
    env: Env
    bot: BotConfig
    boosty: BoostyConfig
    smtp: SmtpConfig


def parse_file(config_path: str | pathlib.Path) -> Config:
    if not isinstance(config_path, pathlib.Path):
        config_path = pathlib.Path(config_path)

    with open(config_path, 'r') as file:
        raw_data = yaml.full_load(file)
        return Config(**raw_data)
