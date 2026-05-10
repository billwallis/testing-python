import argparse
import pathlib
import re
import textwrap
from collections.abc import Sequence

SUCCESS = 0
FAILURE = 1
HERE = pathlib.Path(__file__).parent
PROJECTS_PATH = HERE.parent / "src"


def _normalise_name(name: str) -> str:
    if re.match(r"[a-zA-Z0-9_-]", name):
        return name.replace("-", "_")

    raise ValueError(f"{name!r} is not a valid name")


def _add_file(filename: pathlib.Path, content: str | None = None) -> None:
    filename.touch(exist_ok=True)
    if content:
        filename.write_text(content, encoding="utf-8")


def add_project(project_name: str) -> int:
    print(project_name)
    project_path = PROJECTS_PATH / _normalise_name(project_name)
    project_path.mkdir(parents=True, exist_ok=True)

    _add_file(project_path / "__init__.py")
    _add_file(project_path / "main.py")
    _add_file(
        filename=project_path / "pyproject.toml",
        content=textwrap.dedent(
            f"""\
            # yaml-language-server: $schema=https://json.schemastore.org/pyproject.json

            [project]
            name = "{project_name}"
            version = "0.0.0"
            """
        ),
    )

    return SUCCESS


def main(argv: Sequence[str] | None = None) -> int:
    """
    Parse the arguments and run the command.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("project-names", nargs="*")

    args = parser.parse_args(argv)
    outcome = SUCCESS
    for project_name in getattr(args, "project-names"):
        outcome |= add_project(project_name)

    return SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())  # pragma: no cover
