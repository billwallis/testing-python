"""
https://youtu.be/oAkLSJNr5zY?si=5n5ytU5MssdzDqS2
"""

import asyncio
import concurrent.futures
import datetime
import os
import random
import time

IO_LIMIT = 2
CPU_LIMIT = os.cpu_count()
NOW = datetime.datetime.now


async def do_io_bound_work__async(
    semaphore: asyncio.Semaphore,
    task_id: int,
) -> None:
    async with semaphore:
        print(f"\tDoing work for task {task_id}...")
        await asyncio.sleep(random.randrange(0, 5))  # noqa: S311
        print(f"\tFinished work for task {task_id}!")


def do_io_bound_work__sync(task_id: int) -> None:
    print(f"\tDoing work for task {task_id}...", flush=True)
    time.sleep(random.randrange(0, 5))  # noqa: S311
    print(f"\tFinished work for task {task_id}!", flush=True)


def do_cpu_bound_work(task_id: int) -> None:
    print(f"\tDoing work for task {task_id}...", flush=True)
    _ = list(range(100_000_000))  # ~1 second
    print(f"\tFinished work for task {task_id}!", flush=True)


async def main() -> int:
    # Async IO work
    print(f"Doing async IO work with {IO_LIMIT} threads  ({NOW()})")
    s = time.perf_counter()
    semaphore = asyncio.Semaphore(IO_LIMIT)
    tasks = [
        asyncio.create_task(do_io_bound_work__async(semaphore, i))
        for i in range(5)
    ]
    await asyncio.gather(*tasks, return_exceptions=True)
    print(
        f"Async IO work took {time.perf_counter() - s:.2f} seconds  ({NOW()})\n"
    )

    # Sync IO work
    print(f"Doing sync IO work  ({NOW()})")
    s = time.perf_counter()
    # TODO: how can we use a semaphore here?
    async with asyncio.TaskGroup() as tg:
        [
            tg.create_task(asyncio.to_thread(do_io_bound_work__sync, i))
            for i in range(5)
        ]
    print(
        f"Sync IO work took {time.perf_counter() - s:.2f} seconds  ({NOW()})\n"
    )

    # CPU work
    print(f"Doing CPU work with {CPU_LIMIT} processes  ({NOW()})")
    s = time.perf_counter()
    loop = asyncio.get_running_loop()
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=CPU_LIMIT
    ) as executor:
        tasks = [
            loop.run_in_executor(executor, do_cpu_bound_work, i)
            for i in range(5)
        ]
        await asyncio.gather(*tasks, return_exceptions=True)
    print(f"CPU work took {time.perf_counter() - s:.2f} seconds  ({NOW()})")

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
