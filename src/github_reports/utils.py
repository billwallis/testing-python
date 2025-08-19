import contextlib
import json
import os
import pathlib

import github

RED = "\033[1;31m"
GREEN = "\033[1;32m"
GREY = "\033[38;5;240m"
BOLD = "\033[1m"
RESET = "\033[0m"
HERE = pathlib.Path(__file__).parent


def colour(text: str, colour_: str) -> str:
    """
    Return the text in the given colour.
    """

    return f"{colour_}{text}{RESET}"


class Context:
    _resource_path: pathlib.Path

    def __init__(self, **kwargs):
        self._resource_path = HERE

        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def resource_path(self) -> pathlib.Path:
        return self._resource_path

    @resource_path.setter
    def resource_path(self, path: pathlib.Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        self._resource_path = path


class ReprEncoder(json.JSONEncoder):
    def default(self, o):
        return repr(o)


@contextlib.contextmanager
def github_connection():
    """
    Return a context manager for a GitHub connection.
    """

    gh = github.Github(
        auth=github.Auth.Token(os.environ["GITHUB_TOKEN"]),
    )
    yield gh
    gh.close()
