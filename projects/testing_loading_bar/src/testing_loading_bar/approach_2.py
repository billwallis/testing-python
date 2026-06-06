import contextlib
import random
import time
from collections.abc import Callable, Generator

LOADING_BAR_EMPTY = "░"
LOADING_BAR_FULL = "▓"


def _loading_bar(percentage: float, width: int) -> str:
    full_bars = round(width * percentage)
    empty_bars = width - full_bars
    return full_bars * LOADING_BAR_FULL + empty_bars * LOADING_BAR_EMPTY


@contextlib.contextmanager
def loading_bar_ctx(width: int) -> Generator[Callable[[float], None]]:
    yield lambda percent: print(
        f"\r{_loading_bar(percent, width)} {100 * percent:.0f}%",
        end="",
    )


def main() -> int:
    i, n = 0, 100
    with loading_bar_ctx(width=24) as bar:
        while i <= n:
            perc = i / n
            bar(perc)
            if random.random() < 0.01:  # noqa: S311, PLR2004
                i += 1
                time.sleep(0.1)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
