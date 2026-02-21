from __future__ import annotations

import dataclasses
import datetime
import functools
import json
import os
import pathlib
from collections.abc import Callable
from typing import Any

import requests

REST_API_BASE_URL = "https://api.github.com"
GRAPHQL_API_BASE_URL = "https://api.github.com/graphql"
DEFAULT_TIMEOUT_SECONDS = 60
DEFAULT_PAGE_SIZE = 50
MAX_RETRIES = 5


def retry(
    exceptions: type[Exception] | tuple[type[Exception], ...],
    times: int = MAX_RETRIES,
) -> Callable[..., Callable[..., Any]]:
    """
    Source - https://stackoverflow.com/a/64030200
    Posted by mrkiril
    Retrieved 2026-02-09, License - CC BY-SA 4.0
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 0
            while attempt < times:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    print(
                        f"Exception thrown {type(e).__name__} when attempting to run %s,"
                        " attempt %d of %d" % (func, attempt, times)
                    )
                    attempt += 1
            return func(*args, **kwargs)

        return wrapper

    return decorator


@dataclasses.dataclass
class PageInfo:
    end_cursor: str
    start_cursor: str
    has_previous_page: bool
    has_next_page: bool

    @classmethod
    def from_json(cls, page_info: dict[str, str | bool]) -> PageInfo:
        return cls(
            end_cursor=page_info.get("endCursor", ""),
            start_cursor=page_info.get("startCursor", ""),
            has_previous_page=page_info.get("hasPreviousPage", False),
            has_next_page=page_info.get("hasNextPage", False),
        )


@dataclasses.dataclass
class RateLimit:
    limit: int
    cost: int
    remaining: int
    reset_at: str

    @classmethod
    def from_json(
        cls,
        rate_limit: dict[str, str | bool | datetime.datetime],
    ) -> RateLimit:
        return cls(
            limit=rate_limit.get("limit", -1),
            cost=rate_limit.get("cost", -1),
            remaining=rate_limit.get("remaining", -1),
            reset_at=rate_limit.get("resetAt", str(datetime.datetime.now())),
        )

    def display(self) -> str:
        return f"cost {self.cost}, remaining {self.remaining}, reset at {self.reset_at}"


class GitHubClient:
    def __init__(self, api_token: str) -> None:
        self._api_token = api_token

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_token}",
            "Content-Type": "application/json",
        }

    @retry(
        times=3,
        exceptions=(
            requests.exceptions.JSONDecodeError,
            requests.exceptions.ChunkedEncodingError,
        ),
    )
    def _graphql(
        self,
        query: str,
        variables: dict[str, Any],
    ) -> Any:
        """
        Execute a GraphQL query against GitHub.

        https://docs.github.com/en/graphql/reference
        """

        response = requests.post(
            url=GRAPHQL_API_BASE_URL,
            headers=self.headers,
            json={
                "query": query,
                "variables": variables,
            },
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )

        return response.json()

    def graphql(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
    ) -> list[Any]:
        """
        Execute a GraphQL query against GitHub.

        Paginated results are continued until all results have been retrieved.
        """

        if variables is None:
            variables = {}

        query_vars = {
            "page_size": DEFAULT_PAGE_SIZE,
            "page_after": "",
        } | variables

        pages = []
        more_pages = True
        while more_pages:
            # print("Executing with vars:", query_vars)

            response = self._graphql(
                query=query,
                variables=query_vars,
            )
            if errors := response.get("errors"):
                raise ValueError(json.dumps(errors, indent=2))
            data = response["data"]

            pages.append(data)

            page_info = _extract_page_info(data)
            query_vars["page_after"] = page_info.end_cursor
            more_pages = page_info.has_next_page

            # print(RateLimit.from_json(response["data"]["rateLimit"]).display())

        return pages


def _extract_page_info(data: dict) -> PageInfo:
    """
    Extract the pagination information from the response.

    Note: this only supports a single paginated query.
    """

    def _walk_dict(dict_: dict) -> dict:
        try:
            page_info = dict_["pageInfo"]
            assert isinstance(page_info, dict)  # noqa: S101
            return page_info
        except KeyError:
            for k in dict_.values():
                if page_info := _walk_dict(k):
                    return page_info
        except TypeError:
            return {}

        return {}  # Why is this needed by the type checker? Anything here would be an exception, so no return

    return PageInfo.from_json(_walk_dict(data))


if __name__ == "__main__":
    queries = pathlib.Path(__file__).parent / "queries"
    gh = GitHubClient(api_token=os.environ["GITHUB_TOKEN"])
    here = pathlib.Path(__file__).parent

    resp = gh.graphql(
        query=(queries / "organisation.graphql").read_text(),
        variables={"organisation": "TasmanAnalytics"},
    )
    # print(json.dumps(resp, indent=2))
    (here / "organisation.json").write_text(json.dumps(resp, indent=2))

    resp = gh.graphql(
        query=(queries / "organisation-repositories.graphql").read_text(),
        variables={
            "organisation": "TasmanAnalytics",
        },
    )
    # print(json.dumps(resp, indent=2))
    (here / "organisation-repositories.json").write_text(
        json.dumps(resp, indent=2)
    )

    resp = gh.graphql(
        query=(queries / "repository.graphql").read_text(),
        variables={
            "organisation": "TasmanAnalytics",
            "repository": "dbt-datadict",
        },
    )
    # print(json.dumps(resp, indent=2))
    (here / "repository.json").write_text(json.dumps(resp, indent=2))

    resp = gh.graphql(
        query=(queries / "repository-branches.graphql").read_text(),
        variables={
            "organisation": "TasmanAnalytics",
            "repository": "dbt-datadict",
        },
    )
    # print(json.dumps(resp, indent=2))
    (here / "repository-branches.json").write_text(json.dumps(resp, indent=2))

    resp = gh.graphql(
        query=(queries / "repository-pull-requests.graphql").read_text(),
        variables={
            "organisation": "TasmanAnalytics",
            "repository": "dbt-datadict",
        },
    )
    # print(json.dumps(resp, indent=2))
    (here / "repository-pull-requests.json").write_text(
        json.dumps(resp, indent=2)
    )

    resp = gh.graphql(
        query=(queries / "organisation-teams.graphql").read_text(),
        variables={
            "organisation": "TasmanAnalytics",
            "repository": "dbt-datadict",
        },
    )
    # print(json.dumps(resp, indent=2))
    (here / "organisation-teams.json").write_text(json.dumps(resp, indent=2))
