"""
Create Avro files for DuckDB to read.
"""

import functools
import pathlib

import avro.datafile
import avro.io
import avro.schema

HERE = pathlib.Path(__file__).parent
SCHEMAS = HERE / "schemas"


@functools.cache
def get_schema(schema_name: str) -> avro.schema.Schema:
    """
    Get the Avro schema from a file.
    """

    return avro.schema.parse(
        (SCHEMAS / schema_name).read_text(encoding="utf-8")
    )


def create_avro_file(target: pathlib.Path, data: list) -> None:
    """
    Create an Avro file with some records.
    """

    with avro.datafile.DataFileWriter(
        open(target, "wb"),
        avro.io.DatumWriter(),
        get_schema("model.avsc"),
    ) as writer:
        for record in data:
            writer.append(record)


def main() -> None:
    create_avro_file(
        target=HERE / "models-01.avro",
        data=[
            {
                "name": "users",
                "description": "user details",
                "columns": ["id", "name"],
            },
            {
                "name": "payments",
                "description": "payment details",
                "columns": ["id", "amount", "user_id"],
            },
        ],
    )
    create_avro_file(
        target=HERE / "models-02.avro",
        data=[
            {
                "name": "foo",
                "enabled": False,
                "description": "something",
                "columns": ["a", "b", "c"],
            },
            {
                "name": "bar",
                "enabled": False,
                "description": "something else",
                "columns": ["x", "y", "z"],
            },
        ],
    )


if __name__ == "__main__":
    main()
