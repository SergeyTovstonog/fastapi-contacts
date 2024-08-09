from fastapi_cache import FastAPICache


async def invalidate_contacts_cache():
    await FastAPICache.clear(namespace="get_contacts")
