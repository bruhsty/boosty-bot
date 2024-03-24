from typing import Literal, Sequence

import httpx
from registration.domain.models import BoostyProfile

from .models import GetSubscribersListResponse


class InvalidBoostyCredentialsError(Exception):
    pass


class BoostyAPI:
    BASE_URL = r"https://api.boosty.to/v1"

    def __init__(
        self, access_token: str, refresh_token: str, client: httpx.AsyncClient | None = None
    ) -> None:
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.client = client or httpx.AsyncClient()

    async def get_subscribers_list(
        self,
        user: str,
        sort_by: Literal["payments", "on_time"] = "on_time",
        order: Literal["lt", "gt"] = "gt",
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[BoostyProfile]:
        url = self.BASE_URL + f"/blog/{user}/subscribers"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        }
        params = {
            "sort_by": sort_by,
            "order": order,
            "limit": limit,
            "offset": offset,
        }
        response = await self.client.get(url, params=params, headers=headers)
        if response.status_code == 401:
            raise InvalidBoostyCredentialsError("Access token is invalid or expired")
        data = response.read()

        return self.parse_subscriber_list_data(data)

    @classmethod
    def parse_subscriber_list_data(cls, data: bytes) -> Sequence[BoostyProfile]:
        return GetSubscribersListResponse.model_validate_json(data).to_model()
