from contextlib import asynccontextmanager
from fastapi_cache import FastAPICache
from fastapi import FastAPI

from redis import asyncio as aioredis
from fastapi_cache.backends.redis import RedisBackend

from config.general import settings
from src.contacts.routers import router as router_contacts
from src.auth.routers import router as router_auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    redis = aioredis.from_url(settings.redis_url, encoding="utf-8")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield
    # Shutdown event
    await redis.close()

app = FastAPI(lifespan=lifespan)

app.include_router(router_contacts, prefix="/contacts", tags=["contacts"])
app.include_router(router_auth, prefix="/auth", tags=["auth"])

@app.get('/ping')
async def ping():
    return {'message': 'pong'}

