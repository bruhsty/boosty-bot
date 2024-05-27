import enum
import pathlib

import yaml
from pydantic import BaseModel, Extra
from pydantic_settings import BaseSettings

__all__ = ["Config", "parse_file", "UpdateType", "Env", "Channel"]


class Env(str, enum.Enum):
    PROD = "prod"
    DEV = "prod"
    TEST = "test"


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


class Channel(BaseModel):
    id: int
    invite_link: str
    level_id: int


class BotConfig(BaseSettings):
    token: str
    updates: UpdateType
    webhook: WebhookConfig | None
    polling: PollingConfig | None
    channels: list[Channel]


class BoostyConfig(BaseSettings):
    author: str
    access_token: str
    refresh_token: str


class SmtpConfig(BaseSettings):
    host: str
    port: int
    username: str
    password: str
    use_tls: bool = True


class RedisConfig(BaseModel):
    host: str
    port: int
    db: int
    password: str | None = None


class DataBaseConfig(BaseSettings):
    host: str
    port: int
    username: str
    password: str
    database: str
    ssl_mode: str


class Config(BaseSettings, extra=Extra.allow):
    env: Env
    bot: BotConfig
    boosty: BoostyConfig
    smtp: SmtpConfig
    database: DataBaseConfig
    redis: RedisConfig


def parse_file(config_path: str | pathlib.Path) -> Config:
    if not isinstance(config_path, pathlib.Path):
        config_path = pathlib.Path(config_path)

    with open(config_path, "r") as file:
        raw_data = yaml.full_load(file)
        return Config(**raw_data)
