import pathlib

import pytest
import faker
import yaml

from bruhsty import config


@pytest.fixture(scope='function')
def valid_config_data(fake: faker.Faker) -> dict:
    return {
        "boosty": {
            "email": fake.email(),
            "password": fake.password(),
        },
        "bot": {
            "token": fake.pystr(min_chars=20, max_chars=20)
        }
    }


@pytest.fixture(scope='function')
def valid_config_path(
        tmp_path: pathlib.Path,
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
