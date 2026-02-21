"""
Demonstrate how to use Jinja2 with SQL.
"""

import pathlib

import jinja2

HERE = pathlib.Path(__file__).parent


def main() -> None:
    sql = (HERE / "example.sql").read_text(encoding="utf-8")
    print(jinja2.Template(sql).render())


if __name__ == "__main__":
    main()
