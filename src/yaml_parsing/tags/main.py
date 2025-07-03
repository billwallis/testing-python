"""
PyYAML adheres to the YAML 1.1 specification.
ruamel.yaml adheres to the YAML 1.2 specification by default (and supports 1.1).

There's a big difference between the two specs for boolean values:

- https://yaml.org/type/bool.html
- https://yaml.org/spec/1.2.2/#10212-boolean
"""

import dataclasses
import pathlib
from collections.abc import Callable

import ruamel.yaml as ruyaml
import yaml  # pyyaml

GREEN = "\033[1;32m"
BLUE = "\033[1;34m"
RESET = "\033[0m"
HERE = pathlib.Path(__file__).parent


def colour(text: str, colour_: str) -> str:
    """
    Return the text in the given colour.
    """

    return f"{colour_}{text}{RESET}"


def print_values(content: str, loader: Callable) -> None:
    """
    Print the values of a YAML document using the specified loader.
    """

    for document in loader(content):
        for item in document.items():
            print(f"  {item[0]}:")
            for k, v in item[1].items():
                col = BLUE if isinstance(v, bool) else GREEN
                print(f"    {k}: {colour(v, col)}")


def bools_example(content: str):
    """
    Compare boolean value serialisation between ruamel.yaml and PyYAML.
    """

    print("\nUsing ruamel.yaml:")
    print_values(content, ruyaml.YAML(typ="safe", pure=True).load_all)

    print("\nUsing PyYAML:")
    print_values(content, yaml.safe_load_all)


@dataclasses.dataclass
class Model:
    name: str
    archived: bool
    columns: list[str]


def python_example__simple(content: str):
    """
    Serialise YAML content to a Python object.
    """

    print("\nUsing ruamel.yaml:")
    print("   ", ruyaml.YAML(typ="unsafe").load(content))

    print("\nUsing PyYaml:")
    print("   ", yaml.load(content, Loader=yaml.Loader))  # noqa: S506


def python_example__complex():
    """
    Outsource to:

    - https://github.com/TasmanAnalytics/openapi-sample/tree/main/src/catalogue
    """


def main():
    bools_example((HERE / "bools.yaml").read_text())
    bools_example((HERE / "bools-tagged.yaml").read_text())
    python_example__simple((HERE / "python-tag.yaml").read_text())


if __name__ == "__main__":
    main()
