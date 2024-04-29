from common.adapters.boosty import BoostyAPI

from boosty.adapters.storage import BoostyProfileStorage


async def update_storage(
    author: str,
    api: BoostyAPI,
    storage: BoostyProfileStorage,
) -> None:
    batch_size = 30
    offset = 0
    while True:
        profiles_batch = await api.get_subscribers_list(
            user=author,
            sort_by="payments",
            order="lt",
            limit=batch_size,
            offset=offset,
        )
        if not profiles_batch:
            break

        await storage.add(*profiles_batch)
