import pytest

import faker


@pytest.fixture(scope='function')
def fake() -> faker.Faker:
    return faker.Faker()
