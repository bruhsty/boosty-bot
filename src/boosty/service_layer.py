import asyncio
import logging
from datetime import timedelta
from typing import Protocol

from common.adapters.boosty import BoostyAPI
from user.domain.models import BoostyProfile

logger = logging.getLogger()


class ProfileStorage(Protocol):
    async def add(self, *profiles: BoostyProfile) -> None: ...


class BoostyProfileUpdater:
    def __init__(
        self,
        author: str,
        api_client: BoostyAPI,
        profile_storage: ProfileStorage,
        period: timedelta,
    ) -> None:
        self.author = author
        self.storage = profile_storage
        self.api_client = api_client
        self.period = period
        self._running = False

    async def run(self) -> None:
        if self._running:
            raise RuntimeError("Updater is already running")

        self._running = True
        while self._running:
            try:
                await asyncio.shield(self.update_storage())
                await asyncio.sleep(self.period.total_seconds())
            except (asyncio.CancelledError, KeyboardInterrupt):
                self._running = False
            except Exception as e:
                logger.error("Failed to update storage", exc_info=e)

    async def update_storage(self) -> None:
        batch_size = 30
        offset = 0
        batch_number = 1
        while True:
            profiles_batch = await self.api_client.get_subscribers_list(
                user=self.author,
                sort_by="payments",
                order="lt",
                limit=batch_size,
                offset=offset,
            )
            logger.info(f"Fetched {batch_number} batch of {len(profiles_batch)} subscribers")

            if not profiles_batch:
                break
            offset += batch_size

            await self.storage.add(*profiles_batch)
            logger.info(f"Batch {batch_number} successfully saved")
            batch_number += 1
