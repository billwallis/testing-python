import arguably

from src.github_reports import reports


@arguably.command
def __root__() -> None:  # noqa: N807
    if arguably.is_target():
        print("use 'gh-report --help' to see available commands")


@arguably.command
def org(organisation_name: str) -> None:
    """
    Generate a report for the given GitHub organisation.

    :param organisation_name: The name of the GitHub organisation to report
        on.
    """

    return reports.org(organisation_name)


@arguably.command
def repo(repository_name: str) -> None:
    """
    Generate a report for the given GitHub repository.

    :param repository_name: The name of the GitHub repository to report on.
    """

    return reports.repo(repository_name)


if __name__ == "__main__":
    arguably.run(name="gh-report")
