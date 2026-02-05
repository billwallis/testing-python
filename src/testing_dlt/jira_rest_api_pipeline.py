import dlt
from dlt.sources.helpers.rest_client.auth import HttpBasicAuth
from dlt.sources.rest_api import rest_api_source


def main():
    subdomain = dlt.secrets["sources.jira.subdomain"]
    email = dlt.secrets["sources.jira.email"]
    api_token = dlt.secrets["sources.jira.api_token"]
    source = rest_api_source(
        {
            "client": {
                "base_url": f"https://{subdomain}.atlassian.net/rest/agile/1.0/",
                "auth": HttpBasicAuth(username=email, password=api_token),
                "paginator": {
                    "type": "auto",
                },
            },
            "resources": [  # type: ignore
                {
                    "name": "board",
                    "endpoint": {
                        "path": "board",
                        "params": {
                            "type": "scrum",
                        },
                    },
                },
                {
                    "name": "sprint",
                    "endpoint": {
                        "path": "board/{resources.board.id}/sprint",
                    },
                },
            ],
        }
    )

    pipeline = dlt.pipeline(
        pipeline_name="jira_rest_api_pipeline",
        destination="duckdb",
        dataset_name="jira_rest_api",
    )

    return pipeline.run(source)


if __name__ == "__main__":
    print(main())
