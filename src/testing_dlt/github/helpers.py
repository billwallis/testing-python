from collections.abc import Iterator

from dlt.common.typing import DictStrAny, StrAny
from dlt.sources.helpers import requests

from . import queries
from .settings import GRAPHQL_API_BASE_URL, REST_API_BASE_URL


#
# Shared
#
def _get_auth_header(access_token: str | None) -> StrAny:
    if access_token:
        return {"Authorization": f"Bearer {access_token}"}
    # REST API works without access token (with high rate limits)
    return {}


#
# Rest API helpers
#
def get_rest_pages(
    access_token: str | None, query: str
) -> Iterator[list[StrAny]]:
    def _request(page_url: str) -> requests.Response:
        r = requests.get(page_url, headers=_get_auth_header(access_token))
        print(
            f"got page {page_url}, requests left: "
            + r.headers["x-ratelimit-remaining"]
        )
        return r

    next_page_url = REST_API_BASE_URL + query
    while True:
        r: requests.Response = _request(next_page_url)
        page_items = r.json()
        if len(page_items) == 0:
            break
        yield page_items
        if "next" not in r.links:
            break
        next_page_url = r.links["next"]["url"]


#
# GraphQL API helpers
#
def get_stargazers(
    owner: str,
    name: str,
    access_token: str,
    items_per_page: int,
    max_items: int | None,
) -> Iterator[Iterator[StrAny]]:
    variables = {"owner": owner, "name": name, "items_per_page": items_per_page}
    for page_items in _get_graphql_pages(
        access_token,
        queries.STARGAZERS_QUERY,
        variables,
        "stargazers",
        max_items,
    ):
        yield page_items


def get_deployments(
    owner: str,
    name: str,
    access_token: str,
    page_size: int,
    max_items: int | None,
) -> Iterator[Iterator[StrAny]]:
    variables = {"owner": owner, "name": name, "page_size": page_size}
    for page_items in _get_graphql_pages(
        access_token,
        queries.DEPLOYMENTS_QUERY,
        variables,
        "deployments",
        max_items,
    ):
        yield page_items


def get_default_branch_commits(
    owner: str,
    name: str,
    access_token: str,
    page_size: int,
    max_items: int | None,
) -> Iterator[Iterator[StrAny]]:
    variables = {"owner": owner, "name": name, "page_size": page_size}
    for page_items in _get_graphql_pages(
        access_token,
        queries.DEFAULT_BRANCH_COMMITS,
        variables,
        "history",
        max_items,
    ):
        yield page_items


def get_repositories(
    owner: str,
    access_token: str,
    page_size: int,
    max_items: int | None,
) -> Iterator[Iterator[StrAny]]:
    variables = {"owner": owner, "page_size": page_size}
    for page_items in _get_graphql_pages(
        access_token,
        queries.REPOSITORIES,
        variables,
        "repositories",
        max_items,
    ):
        yield page_items


def get_reactions_data(
    node_type: str,
    owner: str,
    name: str,
    access_token: str,
    items_per_page: int,
    max_items: int | None,
) -> Iterator[Iterator[StrAny]]:
    variables = {
        "owner": owner,
        "name": name,
        "issues_per_page": items_per_page,
        "first_commits": 100,
        "node_type": node_type,
    }
    for page_items in _get_graphql_pages(
        access_token,
        {
            "issues": queries.ISSUES_QUERY,
            "pullRequests": queries.PULL_REQUESTS_QUERY,
        }[node_type],
        variables,
        node_type,
        max_items,
    ):
        yield page_items


def _extract_top_connection(data: StrAny, node_type: str) -> StrAny:
    assert isinstance(data, dict) and len(data) == 1, (
        f"The data with list of {node_type} must be a dictionary and contain only one element"
    )
    next_data = next(iter(data.values()))
    try:
        return next_data[node_type]
    except KeyError:
        return _extract_top_connection(next_data, node_type)


def _run_graphql_query(
    access_token: str, query: str, variables: DictStrAny
) -> tuple[StrAny, StrAny]:
    def _request() -> requests.Response:
        r = requests.post(
            GRAPHQL_API_BASE_URL,
            json={"query": query, "variables": variables},
            headers=_get_auth_header(access_token),
        )
        return r

    data = _request().json()
    if "errors" in data:
        raise ValueError(data)
    data = data["data"]
    # pop rate limits
    rate_limit = data.pop("rateLimit", {"cost": 0, "remaining": 0})
    return data, rate_limit


def _get_graphql_pages(
    access_token: str,
    query: str,
    variables: DictStrAny,
    node_type: str,
    max_items: int,
) -> Iterator[list[DictStrAny]]:
    items_count = 0
    while True:
        data, rate_limit = _run_graphql_query(access_token, query, variables)
        top_connection = _extract_top_connection(data, node_type)
        data_items = (
            top_connection["nodes"]
            if "nodes" in top_connection
            else top_connection["edges"]
        )
        items_count += len(data_items)
        print(
            f"Got {len(data_items)}/{items_count} {node_type}s, query cost {rate_limit['cost']}, remaining credits: {rate_limit['remaining']}"
        )
        if data_items:
            yield data_items
        else:
            return
        # print(data["repository"][node_type]["pageInfo"]["endCursor"])
        variables["page_after"] = _extract_top_connection(data, node_type)[
            "pageInfo"
        ]["endCursor"]
        if max_items and items_count >= max_items:
            print(f"Max items limit reached: {items_count} >= {max_items}")
            return
