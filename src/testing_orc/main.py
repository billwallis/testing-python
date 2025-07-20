"""
Following the Orc docs at:

- https://orc.apache.org/docs/pyarrow.html

Orc is good columnar storage format, like Parquet.

----

For Windows:

    $Env:TZDIR = "<path to venv>\\.venv\\Lib\\site-packages\\tzdata\\zoneinfo"
    python -m src.testing_orc.main
"""

import pathlib

import pyarrow
import pyarrow.orc

HERE = pathlib.Path(__file__).parent
TARGET = HERE / "example.orc"


def create_orc_file() -> None:
    """
    Create an Orc file with some records.

    Note that Orc does not support appending.
    """

    pyarrow.orc.write_table(
        table=pyarrow.table({"col1": [1, 2, 3], "col2": ["a", "b", None]}),
        where=str(TARGET.absolute()),
        compression="zstd",
    )


def print_metadata() -> None:
    """
    Print the metadata for the Orc file.
    """

    data = pyarrow.orc.ORCFile(str(TARGET))
    print(data.metadata)
    print(f"\nschema\n{data.schema}")
    print(f"\nrows: {data.nrows}")
    # print(data.read())


def print_contents() -> None:
    """
    Print the contents of the Orc file.
    """

    # print(pyarrow.orc.read_table(TARGET))
    [print(row) for row in pyarrow.orc.read_table(TARGET).to_pylist()]


def main():
    create_orc_file()
    # print_metadata()
    print_contents()


if __name__ == "__main__":
    main()
