"""Клиент Redis"""

import redis.asyncio as redis
from app.core.config import settings

redis_client = None

if settings.REDIS_URL:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

async def get_redis():
    return redis_client