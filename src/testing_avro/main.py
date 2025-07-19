"""
Following the Avro docs at:

- https://avro.apache.org/docs/1.11.1/getting-started-python/

Avro is good for serializing data in a compact binary format.

Note that Avro files can only be written to with a single schema, but
they can be read with multiple schemas.
"""

import functools
import pathlib
import random

import avro.datafile
import avro.io
import avro.schema

HERE = pathlib.Path(__file__).parent
SCHEMAS = HERE / "schemas"
TARGET = HERE / "users.avro"


@functools.cache
def get_schema(schema_name: str) -> avro.schema.Schema:
    """
    Get the Avro schema from a file.
    """

    return avro.schema.parse(
        (SCHEMAS / schema_name).read_text(encoding="utf-8")
    )


def create_avro_file():
    """
    Create an Avro file with some records.
    """

    writer = avro.datafile.DataFileWriter(
        open(TARGET, "wb"),
        avro.io.DatumWriter(),
        get_schema("user-v1.avsc"),
    )
    writer.append(
        {
            "name": "Alyssa",
            "favorite_number": 256,
        }
    )
    writer.append(
        {
            "name": "Ben",
            "favorite_number": random.randint(1, 10),
            "favorite_color": "red",
        }
    )
    writer.close()

    appender = avro.datafile.DataFileWriter(
        open(TARGET, "ab+"),
        avro.io.DatumWriter(),
    )
    appender.append(
        {
            "name": "Chrissie",
            "favorite_number": random.randint(1, 10),
        }
    )
    appender.append(
        {
            "name": "Darcy",
        }
    )
    appender.close()


def print_contents(schema: avro.schema.Schema | None = None):
    """
    Print the contents of the Avro file using the given schema.
    """

    reader = avro.datafile.DataFileReader(
        open(TARGET, "rb"),
        avro.io.DatumReader(readers_schema=schema),
    )
    [print(user) for user in reader]
    reader.close()


def main():
    create_avro_file()

    print("\nUsing default schema:")
    print_contents()

    print("\nUsing schema 1:")
    print_contents(schema=get_schema("user-v1.avsc"))

    print("\nUsing schema 2:")
    print_contents(schema=get_schema("user-v2.avsc"))

    print("\nUsing schema 3:")
    print_contents(schema=get_schema("user-v3.avsc"))


if __name__ == "__main__":
    main()
