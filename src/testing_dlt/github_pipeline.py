import dlt
from github import (
    github_default_branch_commits,
    github_deployments,
    github_reactions,
    github_repo_events,
    github_repositories,
    github_stargazers,
)


def _default_pipelines():
    # dev_mode = True
    dev_mode = False

    def load_duckdb_repo_reactions_issues_only() -> None:
        """Loads issues, their comments and reactions for duckdb"""
        pipeline = dlt.pipeline(
            "github_reactions",
            destination="duckdb",
            dataset_name="duckdb_issues",
            dev_mode=dev_mode,
        )
        # get only 100 items (for issues and pull request)
        data = github_reactions(
            "duckdb", "duckdb", items_per_page=100, max_items=100
        ).with_resources("issues")
        print(pipeline.run(data))

    def load_airflow_events() -> None:
        """Loads airflow events. Shows incremental loading. Forces anonymous access token"""
        pipeline = dlt.pipeline(
            "github_events", destination="duckdb", dataset_name="airflow_events"
        )
        data = github_repo_events("apache", "airflow", access_token="")
        print(pipeline.run(data))
        # if you uncomment this, it does not load the same events again
        # data = github_repo_events("apache", "airflow", access_token="")
        # print(pipeline.run(data))

    def load_dlthub_dlt_all_data() -> None:
        """Loads all issues, pull requests and comments for dlthub dlt repo"""
        pipeline = dlt.pipeline(
            "github_reactions",
            destination="duckdb",
            dataset_name="dlthub_reactions",
            dev_mode=dev_mode,
        )
        data = github_reactions("dlt-hub", "dlt")
        print(pipeline.run(data))

    def load_dlthub_dlt_stargazers() -> None:
        """Loads all stargazers for dlthub dlt repo"""
        pipeline = dlt.pipeline(
            "github_stargazers",
            destination="duckdb",
            dataset_name="dlthub_stargazers",
            dev_mode=dev_mode,
        )
        data = github_stargazers("dlt-hub", "dlt")
        print(pipeline.run(data))

    load_duckdb_repo_reactions_issues_only()
    load_airflow_events()
    load_dlthub_dlt_all_data()
    load_dlthub_dlt_stargazers()


def load__tasman_analytics__dbt_datadict():
    """
    Load all data for the TasmanAnalytics/dbt-datadict repo.
    """

    pipeline = dlt.pipeline(
        "github_tasman_analytics",
        destination="duckdb",
        dataset_name="github_repositories",
    )
    data = github_repositories("TasmanAnalytics")
    print(pipeline.run(data))

    pipeline = dlt.pipeline(
        "github_tasman_analytics",
        destination="duckdb",
        dataset_name="github_reactions",
    )
    data = github_reactions("TasmanAnalytics", "dbt-datadict")
    print(pipeline.run(data))

    pipeline = dlt.pipeline(
        "github_tasman_analytics",
        destination="duckdb",
        dataset_name="github_stargazers",
    )
    data = github_stargazers("TasmanAnalytics", "dbt-datadict")
    print(pipeline.run(data))

    pipeline = dlt.pipeline(
        "github_tasman_analytics",
        destination="duckdb",
        dataset_name="github_deployments",
    )
    data = github_deployments("TasmanAnalytics", "dbt-datadict")
    print(pipeline.run(data))

    pipeline = dlt.pipeline(
        "github_tasman_analytics",
        destination="duckdb",
        dataset_name="github_default_branch_commits",
    )
    data = github_default_branch_commits("TasmanAnalytics", "dbt-datadict")
    print(pipeline.run(data))


if __name__ == "__main__":
    # _default_pipelines()
    load__tasman_analytics__dbt_datadict()
