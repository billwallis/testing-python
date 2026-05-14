"""
Test runtime differences with between C and Python.
"""

import dis
import timeit

from testing_cython import (
    cythonisation,
    pure_python,
)

N = 10


def dis_pure_python() -> None:
    print("\nwhile loop")
    dis.dis(pure_python.while_loop)
    print("\nfor loop")
    dis.dis(pure_python.for_loop)
    print("\nsum func")
    dis.dis(pure_python.sum_function)
    print("\nsum calc")
    dis.dis(pure_python.sum_calculation)


def time_pure_python(repeat: int = 1000) -> None:
    # # check that the values all sum correctly
    # print('Check Sums')
    # while_loop(verbose=True)
    # for_loop(verbose=True)
    # sum_function(verbose=True)
    # sum_calculation(verbose=True)

    # perform the speed tests
    print("\nSpeed Test")
    print("while loop:\t", timeit.timeit(pure_python.while_loop, number=repeat))
    print("for loop:\t", timeit.timeit(pure_python.for_loop, number=repeat))
    print("sum func:\t", timeit.timeit(pure_python.sum_function, number=repeat))
    print(
        "sum calc:\t", timeit.timeit(pure_python.sum_calculation, number=repeat)
    )


def time_cython(repeat: int = 1000) -> None:
    # perform the speed tests
    print("\nSpeed Test with C")
    print(
        "while loop:\t",
        timeit.timeit(cythonisation.while_loop_c, number=repeat),
    )
    print("for loop:\t", timeit.timeit(cythonisation.for_loop_c, number=repeat))
    print(
        "sum func:\t",
        timeit.timeit(cythonisation.sum_function_c, number=repeat),
    )
    print(
        "sum calc:\t",
        timeit.timeit(cythonisation.sum_calculation_c, number=repeat),
    )


if __name__ == "__main__":
    # dis_pure_python()
    time_pure_python(1000000)
    time_cython(1000000)
