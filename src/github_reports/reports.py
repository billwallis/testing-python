import json
import os
import pathlib
from typing import Any

import dotenv
import duckdb

from src.github_reports import client, utils

dotenv.load_dotenv()

HERE = pathlib.Path(__file__).parent
QUERIES = HERE / "queries"
DATA = HERE / "data"


def _col_bool(b: bool | None) -> str:
    cols = {
        True: utils.GREEN,
        False: utils.RED,
        None: utils.BOLD + utils.GREY,
    }
    return utils.colour(str(b), cols[b])


def _read_query(query_name: str) -> str:
    return (QUERIES / query_name).read_text(encoding="utf-8")


def _make_dir(dir_path: pathlib.Path) -> pathlib.Path:
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


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


def org(organisation_name: str) -> None:
    """
    Generate a report for the given GitHub organisation.

    :param organisation_name: The name of the GitHub organisation to report
        on.
    """

    gh = client.GitHubClient(api_token=os.environ["GITHUB_TOKEN"])

    # Organisation details
    print("Retrieving organisation details...")
    resp = gh.graphql(
        query=_read_query("organisation.graphql"),
        variables={"organisation": organisation_name},
    )
    assert len(resp) == 1  # noqa: S101
    organisation = resp[0]["organization"]
    organisation_name = organisation["login"]
    data_path = _make_dir(DATA / organisation_name)
    (data_path / "organisation.json").write_text(
        json.dumps(organisation, indent=2)
    )

    # Organisation teams
    print("Retrieving organisation teams...")
    resp = gh.graphql(
        query=_read_query("organisation-teams.graphql"),
        variables={"organisation": organisation_name},
    )
    teams, total_count = [], 0
    for page in resp:
        total_count = page["organization"]["teams"]["totalCount"]
        teams.extend(page["organization"]["teams"]["nodes"])
    (data_path / "organisation-teams.json").write_text(
        json.dumps(teams, indent=2)
    )
    print(
        f"Found {len(teams)} teams in {organisation_name} (expected {total_count})"
    )

    team_repo_permissions = dict()
    for team in teams:
        if team["repositories"]["totalCount"] > 100:  # noqa: PLR2004
            raise RuntimeError(
                f"Not all repositories have been retrieved for team {team['slug']}"
            )

        team_repo_permissions[team["slug"]] = {
            r["node"]["name"]: r["permission"]
            for r in team["repositories"]["edges"]
        }

    # Organisation repositories
    print("Retrieving organisation repositories...")
    resp = gh.graphql(
        query=_read_query("organisation-repositories.graphql"),
        variables={"organisation": organisation_name},
    )
    repositories, total_count = [], 0
    for page in resp:
        total_count = page["organization"]["repositories"]["totalCount"]
        repositories.extend(page["organization"]["repositories"]["nodes"])
    (data_path / "organisation-repositories.json").write_text(
        json.dumps(repositories, indent=2)
    )
    print(
        f"Found {len(repositories)} repositories in {organisation_name} (expected {total_count})"
    )

    # Print key repository details
    for repository in sorted(
        repositories,
        key=lambda r: r["updatedAt"],
        reverse=True,
    ):
        repo_name = repository["name"]
        if repository["isArchived"]:
            print(utils.colour(f"{repo_name}  (archived)", utils.GREY))
            continue

        visibility = "🔒" if repository["visibility"] == "PRIVATE" else "🌐"
        has_admins_as_admin = "ADMIN" == (
            team_repo_permissions.get("admins", {}).get(repo_name, "")
        )
        parts = [
            f"{utils.colour(repo_name, utils.BOLD)} {visibility}  (",
            f"delete branch on merge: {_col_bool(repository['deleteBranchOnMerge'])}",
            f", CODEOWNERS: {_col_bool(repository['planFeatures']['codeowners'])}",
            (
                f", Admins: {_col_bool(has_admins_as_admin)}"
                if organisation_name == "TasmanAnalytics"
                else ""
            ),
            f")  {repository['url']}",
        ]
        print("".join(parts))


def repo(repository_name: str) -> None:
    """
    Generate a report for the given GitHub repository.

    :param repository_name: The name of the GitHub repository to report on.
    """

    gh = client.GitHubClient(api_token=os.environ["GITHUB_TOKEN"])
    _org_name, _repo_name = repository_name.split("/")
    variables = {"organisation": _org_name, "repository": _repo_name}

    # Repository details
    print("Retrieving repository details...")
    resp = gh.graphql(
        query=_read_query("repository.graphql"),
        variables=variables,
    )
    assert len(resp) == 1  # noqa: S101
    repository = resp[0]["repository"]
    repository_name = repository["nameWithOwner"]
    data_path = _make_dir(DATA / repository_name)
    (data_path / "repository.json").write_text(json.dumps(repository, indent=2))
    print(
        f"{repository_name}  (delete branch on merge: {_col_bool(repository['deleteBranchOnMerge'])})"
    )

    # Repository branches
    print("Retrieving repository branches...")
    resp = gh.graphql(
        query=_read_query("repository-branches.graphql"),
        variables=variables,
    )
    branches, total_count = [], 0
    for page in resp:
        total_count = page["repository"]["refs"]["totalCount"]
        branches.extend(page["repository"]["refs"]["nodes"])
    (data_path / "repository-branches.json").write_text(
        json.dumps(branches, indent=2)
    )
    print(
        f"Found {len(branches)} branches in {repository_name} (expected {total_count})"
    )

    # Repository pull requests
    print("Retrieving repository pull requests...")
    resp = gh.graphql(
        query=_read_query("repository-pull-requests.graphql"),
        variables=variables,
    )
    pull_requests, total_count = [], 0
    for page in resp:
        total_count = page["repository"]["pullRequests"]["totalCount"]
        pull_requests.extend(page["repository"]["pullRequests"]["nodes"])
    (data_path / "repository-pull-requests.json").write_text(
        json.dumps(pull_requests, indent=2)
    )
    print(
        f"Found {len(pull_requests)} pull requests in {repository_name} (expected {total_count})"
    )
    print(
        _run_report(
            branches_file=data_path / "repository-branches.json",
            pull_requests_file=data_path / "repository-pull-requests.json",
        )
    )
