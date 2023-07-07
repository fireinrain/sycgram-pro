from time import time
from typing import Union

from .constants import GHOST_INTERVAL, STORE_GHOST_CACHE, STORE_GHOST_DATA
from .storage import SimpleStore


async def get_ghost_to_read(cid: Union[int, str]) -> bool:
    """是否自动标记为已读"""
    async with SimpleStore() as store:
        ghost_cache = store.get_data(STORE_GHOST_CACHE)
        ghost_list = store.get_data(STORE_GHOST_DATA)
        if cid in ghost_list.keys() and (
            not ghost_cache.get(cid) or
            time() - ghost_cache.get(cid) > GHOST_INTERVAL
        ):
            ghost_cache[cid] = time()
            return True

        return False
