import os
import json
from datetime import datetime, UTC

import asyncpg
import aio_pika
import redis.asyncio as redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="v2-order-service")

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/1")
WRITE_DSN = os.getenv("WRITE_DSN", "postgresql://app_user:app_password@postgres-primary:5432/app_db")
READ_DSN = os.getenv("READ_DSN", "postgresql://app_user:app_password@postgres-replica:5432/app_db")
AMQP_URL = os.getenv("AMQP_URL", "amqp://guest:guest@rabbitmq:5672/")

redis_client = redis.from_url(REDIS_URL, decode_responses=True)
write_pool: asyncpg.Pool | None = None
read_pool: asyncpg.Pool | None = None
amqp_conn: aio_pika.RobustConnection | None = None


class OrderIn(BaseModel):
    user_id: int
    amount: float


@app.on_event("startup")
async def startup():
    global write_pool, read_pool, amqp_conn
    write_pool = await asyncpg.create_pool(WRITE_DSN, min_size=2, max_size=5)
    read_pool = await asyncpg.create_pool(READ_DSN, min_size=1, max_size=3)
    amqp_conn = await aio_pika.connect_robust(AMQP_URL)

    async with write_pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
              id BIGSERIAL PRIMARY KEY,
              user_id BIGINT NOT NULL,
              amount NUMERIC(10,2) NOT NULL,
              created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )


@app.post("/orders")
async def create_order(payload: OrderIn):
    # Redis 简单限流：每用户每分钟最多 30 次
    bucket = f"ratelimit:user:{payload.user_id}:{datetime.now(UTC).strftime('%Y%m%d%H%M')}"
    used = await redis_client.incr(bucket)
    if used == 1:
        await redis_client.expire(bucket, 60)
    if used > 30:
        raise HTTPException(status_code=429, detail="too many requests")

    assert write_pool is not None
    async with write_pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO orders(user_id, amount) VALUES($1, $2) RETURNING id, user_id, amount, created_at",
            payload.user_id,
            payload.amount,
        )

    # 发消息到 MQ
    assert amqp_conn is not None
    channel = await amqp_conn.channel()
    await channel.declare_queue("order.created", durable=True)
    await channel.default_exchange.publish(
        aio_pika.Message(body=json.dumps({"event": "order.created", "order_id": row["id"]}).encode()),
        routing_key="order.created",
    )

    return dict(row)


@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    assert read_pool is not None
    async with read_pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, user_id, amount, created_at FROM orders WHERE id=$1", order_id
        )
    if not row:
        raise HTTPException(status_code=404, detail="not found")
    return dict(row)
