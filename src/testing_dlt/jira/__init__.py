"""This source uses Jira API and dlt to load data such as Issues, Users, Workflows and Projects to the database."""

from collections.abc import Iterable

import dlt
from dlt.common.typing import DictStrAny, TDataItem
from dlt.sources import DltResource
from dlt.sources.helpers import requests

from .settings import DEFAULT_ENDPOINTS, DEFAULT_PAGE_SIZE


@dlt.source(max_table_nesting=2)
def jira(
    subdomain: str = dlt.secrets.value,
    email: str = dlt.secrets.value,
    api_token: str = dlt.secrets.value,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> Iterable[DltResource]:
    """
    Jira source function that generates a list of resource functions based on endpoints.

    Args:
        subdomain: The subdomain for the Jira instance.
        email: The email to authenticate with.
        api_token: The API token to authenticate with.
        page_size: Maximum number of results per page
    Returns:
        Iterable[DltResource]: List of resource functions.
    """
    resources = []
    for endpoint_name, endpoint_parameters in DEFAULT_ENDPOINTS.items():
        res_function = dlt.resource(
            get_paginated_data, name=endpoint_name, write_disposition="replace"
        )(
            **endpoint_parameters,  # type: ignore[arg-type]
            subdomain=subdomain,
            email=email,
            api_token=api_token,
            page_size=page_size,
        )
        resources.append(res_function)

    return resources


def get_paginated_data(  # noqa: PLR0913
    subdomain: str,
    email: str,
    api_token: str,
    page_size: int,
    api_path: str = "rest/api/3/search/jql",
    data_path: str | None = None,
    params: DictStrAny | None = None,
) -> Iterable[TDataItem]:
    """
    Function to fetch paginated data from a Jira API endpoint.

    Args:
        subdomain: The subdomain for the Jira instance.
        email: The email to authenticate with.
        api_token: The API token to authenticate with.
        page_size: Maximum number of results per page
        api_path: The API path for the Jira endpoint.
        data_path: Optional data path to extract from the response.
        params: Optional parameters for the API request.
    Yields:
        Iterable[TDataItem]: Yields pages of data from the API.
    """
    url = f"https://{subdomain}.atlassian.net/{api_path}"
    headers = {"Accept": "application/json"}
    auth = (email, api_token)
    params = {} if params is None else params
    params["maxResults"] = page_size
    params["nextPageToken"] = None

    while True:
        response = requests.get(url, auth=auth, headers=headers, params=params)
        response.raise_for_status()
        result = response.json()

        if data_path:
            results_page = result.pop(data_path)
        else:
            results_page = result

        yield results_page

        try:
            next_page_token = result.get("nextPageToken")
        except AttributeError:
            next_page_token = None

        params["nextPageToken"] = next_page_token
        if next_page_token is None:
            break
