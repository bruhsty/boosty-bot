import pytest
import pytest_asyncio
from registration.adapters.boosty import BoostyAPI
from registration.adapters.boosty.api import InvalidBoostyCredentialsError

from config import Config


@pytest_asyncio.fixture(scope="function")
def boosty_api(cfg: Config) -> BoostyAPI:
    return BoostyAPI(access_token=cfg.boosty.access_token, refresh_token=cfg.boosty.refresh_token)


@pytest.mark.asyncio
async def test_boosty_raises_error_if_invalid_credentials_passed(boosty_api: BoostyAPI):
    boosty_api.access_token = "AAAAAAAAAAAA"
    with pytest.raises(InvalidBoostyCredentialsError):
        await boosty_api.get_subscribers_list(
            user="burenotti",
            sort_by="payments",
            order="lt",
            limit=100,
        )


@pytest.mark.asyncio
async def test_boosty_can_retrieve_subscriber_list(boosty_api: BoostyAPI):
    subscribers = await boosty_api.get_subscribers_list(
        user="burenotti",
        sort_by="payments",
        order="lt",
        limit=100,
    )

    assert len(subscribers) == 3
    names = set(sub.name for sub in subscribers)
    assert names == {"Alex Shivilov", "Vit'ka", "Rina Erxori"}
