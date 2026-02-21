"""
https://pypi.org/project/redis/
"""

import asyncio
import time

import redis

STOP_WORD = "exit"


def new_redis_client() -> redis.Redis:
    return redis.Redis(
        host="localhost",
        port=6379,
        db=0,
    )


def basic_example() -> None:
    print("\nBasic example")

    redis_client = new_redis_client()
    redis_client.set("foo", "bar")
    print(redis_client.get("foo"))


def pubsub_example() -> None:
    print("\nPubSub example")

    redis_client = new_redis_client()
    pubsub = redis_client.pubsub()
    pubsub.subscribe("events")
    for message in pubsub.listen():
        if message["type"] == "message":
            content = message["data"].decode("utf-8")
            print(content)
            if content == STOP_WORD:
                break


async def reader(channel: redis.client.PubSub) -> None:
    while True:
        message = await channel.get_message(
            ignore_subscribe_messages=True,
            timeout=0.0,
        )
        if message:
            content = message["data"].decode("utf-8")
            print(content)
            if content == STOP_WORD:
                break


async def async_example() -> None:
    print("\nAsync PubSub example")
    redis_client = await redis.asyncio.from_url("redis://localhost:6379")
    async with redis_client.pubsub() as pubsub:
        await pubsub.subscribe("events")

        future = asyncio.create_task(reader(pubsub))

        await redis_client.publish("events", "Itsy")
        await redis_client.publish("events", "bitsy")
        await redis_client.publish("events", "spider")
        await redis_client.publish("events", "exit")

        await future


def key_expiration_example() -> None:
    print("\nKey expiration example")

    redis_client = new_redis_client()
    redis_client.set("reservation:1", "user:1", ex=1)
    print(redis_client.get("reservation:1"))
    time.sleep(1)
    print(redis_client.get("reservation:1"))


def main() -> None:
    basic_example()
    pubsub_example()
    asyncio.run(async_example())
    key_expiration_example()


if __name__ == "__main__":
    main()
