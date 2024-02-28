import contextlib
import os
import pathlib

import pytest
import faker
import yaml

from bruhsty import config


@contextlib.contextmanager
def update_environ(updates: dict[str, str]) -> dict[str, str]:
    previous_environ = os.environ.copy()
    try:
        os.environ.update(updates)
        yield os.environ
    finally:
        os.environ = previous_environ


@pytest.fixture(scope='function')
def fake() -> faker.Faker:
    return faker.Faker()


@pytest.fixture
def boosty_email(fake: faker.Faker) -> str:
    return fake.email()


@pytest.fixture
def boosty_password(fake: faker.Faker) -> str:
    return fake.password()


@pytest.fixture
def bot_token(fake: faker.Faker) -> str:
    return fake.pystr(min_chars=20, max_chars=20)


@pytest.fixture(scope='function')
def valid_config_data(boosty_email: str, boosty_password: str, bot_token: str) -> dict:
    return {
        "boosty": {
            "email": boosty_email,
            "password": boosty_password,
        },
        "bot": {
            "token": bot_token
        }
    }


@pytest.fixture(scope='function')
def valid_config_path(
        tmp_path: pathlib.Path,
        fake: faker.Faker,
        valid_config_data: dict,
) -> pathlib.Path:
    config_path = tmp_path / 'valid_config.yaml'
    with open(config_path, 'w') as file:
        yaml.dump(valid_config_data, file, indent=4, sort_keys=True)

    return config_path


def test_parse_file(valid_config_path: pathlib.Path, valid_config_data: dict):
    cfg = config.parse_file(valid_config_path)
    assert valid_config_data["bot"]["token"] == cfg.bot.token
    assert valid_config_data["boosty"]["email"] == cfg.boosty.email
    assert valid_config_data["boosty"]["password"] == cfg.boosty.password
