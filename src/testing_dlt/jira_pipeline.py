import dlt
from jira import jira


def load(endpoints: list[str] | None = None) -> None:
    """
    Load data from specified Jira endpoints into a dataset.

    Args:
        endpoints: A list of Jira endpoints. If not provided, defaults to all resources.
    """
    if not endpoints:
        endpoints = list(jira().resources.keys())

    pipeline = dlt.pipeline(
        pipeline_name="jira_pipeline",
        destination="duckdb",
        dataset_name="jira",
    )

    load_info = pipeline.run(jira().with_resources(*endpoints))

    print(f"Load Information: {load_info}")


if __name__ == "__main__":
    # Add your desired endpoints to the list 'endpoints'
    load(endpoints=None)
