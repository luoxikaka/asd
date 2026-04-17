import os
import json
from typing import Any

import asyncpg
import redis.asyncio as redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="v1-min-prod")

INSTANCE_ID = os.getenv("INSTANCE_ID", "unknown")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
DB_DSN = os.getenv(
    "DB_DSN",
    "postgresql://app_user:app_password@postgres:5432/app_db",
)

redis_client: redis.Redis | None = None
pg_pool: asyncpg.Pool | None = None


class ItemIn(BaseModel):
    name: str
    price: float


@app.on_event("startup")
async def startup() -> None:
    global redis_client, pg_pool
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    pg_pool = await asyncpg.create_pool(DB_DSN, min_size=2, max_size=10)

    async with pg_pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id BIGSERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                price NUMERIC(10,2) NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )


@app.on_event("shutdown")
async def shutdown() -> None:
    if redis_client:
        await redis_client.close()
    if pg_pool:
        await pg_pool.close()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "instance": INSTANCE_ID}


@app.post("/items")
async def create_item(payload: ItemIn) -> dict[str, Any]:
    if not pg_pool or not redis_client:
        raise HTTPException(status_code=503, detail="dependencies not ready")

    async with pg_pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO items(name, price) VALUES($1, $2) RETURNING id, name, price, created_at",
            payload.name,
            payload.price,
        )

    item = dict(row)
    cache_key = f"item:{item['id']}"
    await redis_client.set(cache_key, json.dumps(item, default=str), ex=60)

    return {"instance": INSTANCE_ID, "item": item}


@app.get("/items/{item_id}")
async def get_item(item_id: int) -> dict[str, Any]:
    if not pg_pool or not redis_client:
        raise HTTPException(status_code=503, detail="dependencies not ready")

    cache_key = f"item:{item_id}"
    cached = await redis_client.get(cache_key)
    if cached:
        return {"instance": INSTANCE_ID, "source": "redis", "item": json.loads(cached)}

    async with pg_pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, name, price, created_at FROM items WHERE id=$1", item_id
        )

    if not row:
        raise HTTPException(status_code=404, detail="item not found")

    item = dict(row)
    await redis_client.set(cache_key, json.dumps(item, default=str), ex=60)
    return {"instance": INSTANCE_ID, "source": "postgres", "item": item}
