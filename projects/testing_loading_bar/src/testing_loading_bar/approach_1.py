import random
import time

LOADING_BAR_EMPTY = "░"
LOADING_BAR_FULL = "▓"


def _loading_bar(percentage: float, width: int) -> str:
    full_bars = round(width * percentage)
    empty_bars = width - full_bars
    return full_bars * LOADING_BAR_FULL + empty_bars * LOADING_BAR_EMPTY


def _print_loading_bar(percentage: float, width: int = 24) -> None:
    bar = _loading_bar(percentage, width)
    print(f"\r{bar} {100 * percentage:.0f}%", end="", flush=True)


def main() -> int:
    i, n = 0, 100
    while i <= n:
        _print_loading_bar(i / n, 24)
        if random.random() < 0.01:  # noqa: S311, PLR2004
            i += 1
            time.sleep(0.1)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
