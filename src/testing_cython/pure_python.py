N = 1000


def while_loop(verbose: bool = False) -> None:
    total = 0
    i = 0
    while i < N + 1:
        total += i
        i += 1
    if verbose:
        print(total)


def for_loop(verbose: bool = False) -> None:
    total = 0
    for i in range(N + 1):
        total += i
    if verbose:
        print(total)


def sum_function(verbose: bool = False) -> None:
    total = sum(range(N + 1))
    if verbose:
        print(total)


def sum_calculation(verbose: bool = False) -> None:
    total = (N + 1) * N / 2
    if verbose:
        print(total)
