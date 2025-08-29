import contextlib
import functools
import json
import pathlib
from collections.abc import Callable
from typing import Any

import dotenv
import duckdb
import github
from github.Repository import Repository

from src.github_reports import utils

dotenv.load_dotenv()


def _save_all(
    context: utils.Context,
    fetch: Callable[[], Any],
    filename: str,
) -> pathlib.Path:
    outfile = context.resource_path / filename
    outfile.write_text("")
    items = fetch()
    print(f"Found {items.totalCount} {outfile.stem}")
    with outfile.open("a", encoding="utf-8") as f:
        for obj in items:
            f.write(
                json.dumps(obj.__dict__["_rawData"], cls=utils.ReprEncoder)
                + "\n"
            )
    return outfile


def _run_report(
    branches_file: pathlib.Path,
    pull_requests_file: pathlib.Path,
) -> Any:
    """
    Run a report on the repository.
    """

    report_sql = (utils.HERE / "report.sql").read_text()
    replacements = {
        "{{ branches_file }}": str(branches_file),
        "{{ pull_requests_file }}": str(pull_requests_file),
    }
    for placeholder, value in replacements.items():
        report_sql = report_sql.replace(placeholder, value)

    return duckdb.sql(report_sql)


def _has_admins_as_admin(repository: Repository) -> bool:
    """
    Check if the repository has the Admins team as an admin.

    This is specific to the ``TasmanAnalytics`` organisation.
    """

    assert repository.organization.name == "Tasman"  # noqa: S101

    teams = []
    with contextlib.suppress(github.UnknownObjectException):
        teams = list(repository.get_teams())

    return any(
        team.name == "Admins" and team.permission == "admin" for team in teams
    )


def _has_codeowners(repository: Repository) -> bool:
    """
    Check if the repository has a CODEOWNERS file.
    """

    try:
        repository.get_contents(".github/CODEOWNERS")
        return True
    except github.UnknownObjectException:
        return False


def org(organisation_name: str) -> None:
    """
    Generate a report for the given GitHub organisation.

    :param organisation_name: The name of the GitHub organisation to report
        on.
    """

    with utils.github_connection() as gh:
        organisation = gh.get_organization(organisation_name)
        repos = organisation.get_repos(sort="updated", direction="desc")
        print(f"Found {repos.totalCount} repositories in {organisation_name}")
        cols = {
            True: utils.GREEN,
            False: utils.RED,
            None: utils.BOLD + utils.GREY,
        }
        for repository in repos:
            if repository.archived:
                print(
                    utils.colour(f"{repository.name}  (archived)", utils.GREY)
                )
                continue

            def col(b: bool) -> str:
                return utils.colour(str(b), cols[b])

            parts = [
                f"{utils.colour(repository.name, utils.BOLD)}  (",
                f"delete branch on merge: {col(repository.delete_branch_on_merge)}",
                f", CODEOWNERS: {col(_has_codeowners(repository))}",
                f", Admins: {col(_has_admins_as_admin(repository))}"
                if organisation_name == "TasmanAnalytics"
                else "",
                f")  https://github.com/{organisation_name}/{repository.name}",
            ]
            print("".join(parts))


def repo(repository_name: str) -> None:
    """
    Generate a report for the given GitHub repository.

    :param repository_name: The name of the GitHub repository to report on.
    """

    with utils.github_connection() as gh:
        repository = gh.get_repo(repository_name)
        col = utils.GREEN if repository.delete_branch_on_merge else utils.RED
        print(
            f"{repository_name}  (delete branch on merge: {utils.colour(str(repository.delete_branch_on_merge), col)})"
        )

        ctx = utils.Context(resource_path=utils.HERE / "data" / repository_name)
        branches_file = _save_all(
            context=ctx,
            fetch=repository.get_branches,
            filename="branches.jsonl",
        )
        prs_file = _save_all(
            context=ctx,
            fetch=functools.partial(repository.get_pulls, state="all"),
            filename="pull_requests.jsonl",
        )
        print(_run_report(branches_file, prs_file))
