# uv run --env-file 'jira/.env' jira/api.py

import json
import os
import pathlib

import requests
from requests.auth import HTTPBasicAuth

HERE = pathlib.Path(__file__).parent
BASE_URL = os.environ["BASE_URL"]
EMAIL = os.environ["EMAIL"]
API_TOKEN = os.environ["API_TOKEN"]


def get_issue(issue_key: str):
    endpoint = BASE_URL + f"issue/{issue_key}"
    auth = HTTPBasicAuth(EMAIL, API_TOKEN)
    headers = {"Accept": "application/json"}

    response = requests.get(
        endpoint,
        headers=headers,
        auth=auth,
    )

    return response.json()


if __name__ == "__main__":
    issue_id = "DM-109"
    issue_content = get_issue(issue_id)
    # print(issue_content)
    (HERE / f"{issue_id}.json").write_text(json.dumps(issue_content, indent=2))
