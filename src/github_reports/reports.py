import contextlib
import json
import pathlib
from typing import Any

import dotenv
import duckdb
import github
from github.Repository import Repository

from src.github_reports import utils

dotenv.load_dotenv()


def _save_all_branches(
    context: utils.Context,
    repository: Repository,
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
                json.dumps(branch.__dict__["_rawData"], cls=utils.ReprEncoder)
                + "\n"
            )

    return branches_file


def _save_all_prs(
    context: utils.Context, repository: Repository
) -> pathlib.Path:
    """
    Get all pull requests from a repository.
    """

    prs_file = context.resource_path / "prs.jsonl"
    prs_file.write_text("")
    prs = repository.get_pulls(state="all")
    print(f"Found {prs.totalCount} pull requests")

    with prs_file.open("a", encoding="utf-8") as f:
        for i, pr in enumerate(prs, start=1):
            f.write(
                json.dumps(pr.__dict__["_rawData"], cls=utils.ReprEncoder)
                + "\n"
            )

    return prs_file


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

    teams = []
    with contextlib.suppress(github.UnknownObjectException):
        teams = list(repository.get_teams())

    for team in teams:
        if team.name == "Admins" and team.permission == "admin":
            return True
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
            del_col = cols[repository.delete_branch_on_merge]
            has_admins = _has_admins_as_admin(repository)
            print(
                f"{utils.colour(repository.name, utils.BOLD)}  "
                f"(delete branch on merge: {utils.colour(str(repository.delete_branch_on_merge), del_col)}"
                f", Admins: {utils.colour(str(has_admins), cols[has_admins])})  "
                f"https://github.com/{organisation_name}/{repository.name}"
            )


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
        branches_file = _save_all_branches(ctx, repository)
        prs_file = _save_all_prs(ctx, repository)
        print(_run_report(branches_file, prs_file))
