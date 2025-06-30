import contextlib
import json
import os
import pathlib
from typing import Any

import arguably
import dotenv
import duckdb
import github
from github.Repository import Repository

dotenv.load_dotenv()

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
def _github_connection():
    """
    Return a context manager for a GitHub connection.
    """

    gh = github.Github(
        auth=github.Auth.Token(os.environ["GITHUB_TOKEN"]),
    )
    yield gh
    gh.close()


def _save_all_branches(
    context: Context, repository: Repository
) -> pathlib.Path:
    """
    Get all pull requests from a repository.
    """

    branches_file = context.resource_path / "branches.jsonl"
    branches_file.write_text("")
    branches = repository.get_branches()
    print(f"Found {branches.totalCount} branches")

    with branches_file.open("a", encoding="utf-8") as f:
        for i, branch in enumerate(branches, start=1):
            f.write(
                json.dumps(branch.__dict__["_rawData"], cls=ReprEncoder) + "\n"
            )

    return branches_file


def _save_all_prs(context: Context, repository: Repository) -> pathlib.Path:
    """
    Get all pull requests from a repository.
    """

    prs_file = context.resource_path / "prs.jsonl"
    prs_file.write_text("")
    prs = repository.get_pulls(state="all")
    print(f"Found {prs.totalCount} pull requests")

    with prs_file.open("a", encoding="utf-8") as f:
        for i, pr in enumerate(prs, start=1):
            f.write(json.dumps(pr.__dict__["_rawData"], cls=ReprEncoder) + "\n")

    return prs_file


def _run_report(
    branches_file: pathlib.Path,
    pull_requests_file: pathlib.Path,
) -> Any:
    """
    Run a report on the repository.
    """

    report_sql = (HERE / "report.sql").read_text()
    replacements = {
        "{{ branches_file }}": str(branches_file),
        "{{ pull_requests_file }}": str(pull_requests_file),
    }
    for placeholder, value in replacements.items():
        report_sql = report_sql.replace(placeholder, value)

    return duckdb.sql(report_sql)


@arguably.command
def org(organisation_name: str) -> None:
    """
    Generate a report for the given GitHub organisation.

    :param organisation_name: The name of the GitHub organisation to report
        on.
    """

    with _github_connection() as gh:
        organisation = gh.get_organization(organisation_name)
        repos = organisation.get_repos(sort="updated", direction="desc")
        print(f"Found {repos.totalCount} repositories in {organisation_name}")
        cols = {True: GREEN, False: RED, None: BOLD + GREY}
        for repository in repos:
            if repository.archived:
                print(colour(f"{repository.name}  (archived)", GREY))
                continue
            col = cols[repository.delete_branch_on_merge]
            print(
                f"{colour(repository.name, BOLD)}  "
                f"(delete branch on merge: {colour(str(repository.delete_branch_on_merge), col)})  "
                f"https://github.com/{organisation_name}/{repository.name}"
            )


@arguably.command
def repo(repository_name: str) -> None:
    """
    Generate a report for the given GitHub repository.

    :param repository_name: The name of the GitHub repository to report on.
    """

    with _github_connection() as gh:
        repository = gh.get_repo(repository_name)
        col = GREEN if repository.delete_branch_on_merge else RED
        print(
            f"{repository_name}  (delete branch on merge: {colour(str(repository.delete_branch_on_merge), col)})"
        )

        ctx = Context(resource_path=HERE / "data" / repository_name)
        branches_file = _save_all_branches(ctx, repository)
        prs_file = _save_all_prs(ctx, repository)
        print(_run_report(branches_file, prs_file))


@arguably.command
def __root__() -> None:  # noqa: N807
    if arguably.is_target():
        print("use 'gh-report --help' to see available commands")


if __name__ == "__main__":
    arguably.run(name="gh-report")
