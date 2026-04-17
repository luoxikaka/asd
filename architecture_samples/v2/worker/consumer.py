import asyncio
import json
import os

import aio_pika


async def main() -> None:
    conn = await aio_pika.connect_robust(os.getenv("AMQP_URL", "amqp://guest:guest@rabbitmq:5672/"))
    channel = await conn.channel()
    queue = await channel.declare_queue("order.created", durable=True)

    async with queue.iterator() as iterator:
        async for msg in iterator:
            async with msg.process():
                event = json.loads(msg.body.decode())
                print(f"[worker] consume event: {event}")


if __name__ == "__main__":
    asyncio.run(main())
