import os
import json

import redis.asyncio as redis
from fastapi import FastAPI

app = FastAPI(title="v2-user-service")
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"), decode_responses=True)


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    # 缓存示例
    key = f"user:{user_id}"
    cached = await redis_client.get(key)
    if cached:
        return {"source": "redis", "user": json.loads(cached)}

    user = {"id": user_id, "name": f"user-{user_id}", "tier": "pro"}
    await redis_client.set(key, json.dumps(user), ex=120)
    return {"source": "service", "user": user}


@app.get("/health")
async def health():
    return {"ok": True}
