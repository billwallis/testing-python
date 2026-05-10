"""
https://docs.python.org/3/library/struct.html#module-struct

https://stackoverflow.com/a/4915359
"""

import pathlib
import struct
from collections.abc import Callable

HERE = pathlib.Path(__file__).parent
FIXED_WIDTH_FILE = HERE / "example.fwf"
SCHEMA = {
    # column: width
    "employee_id": 8,
    "employee_name": 12,
    "job_name": 12,
    "manager_id": 8,
    "hire_date": 10,
    "salary": 8,
    "commission": 8,
    "department_id": 4,
}


def make_parser(
    field_widths: tuple[int, ...],
) -> Callable[[str], tuple[str, ...]]:
    format_string = " ".join(
        "{}{}".format(abs(fw), "x" if fw < 0 else "s") for fw in field_widths
    )

    def parser(line: str) -> tuple[str, ...]:
        return tuple(
            s.decode()
            for s in struct.Struct(format_string).unpack_from(line.encode())
        )

    return parser


def _stack_overflow_example() -> None:
    fieldwidths = (2, -10, 24)
    parse = make_parser(fieldwidths)
    line = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789\n"
    fields = parse(line)
    print(f"fields: {fields}")


def main() -> int:
    # _stack_overflow_example()

    parser = make_parser(tuple(SCHEMA.values()))
    for line in FIXED_WIDTH_FILE.read_text().rstrip().split("\n"):
        print(parser(line))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
