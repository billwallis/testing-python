ISSUES_QUERY = """
    query($owner: String!, $name: String!, $issues_per_page: Int!, $page_after: String) {
        repository(owner: $owner, name: $name) {
            issues(first: $issues_per_page, orderBy: {field: CREATED_AT, direction: DESC}, after: $page_after) {
                totalCount
                pageInfo {
                    endCursor
                    startCursor
                }
                nodes {
                    number
                    id
                    url
                    title
                    body
                    author {login avatarUrl url}
                    authorAssociation
                    closed
                    closedAt
                    createdAt
                    state
                    updatedAt
                }
            }
        }
        rateLimit {
            limit
            cost
            remaining
            resetAt
        }
    }
"""

PULL_REQUESTS_QUERY = """
    query($owner: String!, $name: String!, $issues_per_page: Int!, $first_commits: Int!, $page_after: String) {
        repository(owner: $owner, name: $name) {
            pullRequests(first: $issues_per_page, orderBy: {field: CREATED_AT, direction: DESC}, after: $page_after) {
                totalCount
                pageInfo {
                    endCursor
                    startCursor
                }
                nodes {
                    number
                    id
                    url
                    title
                    body
                    author {login avatarUrl url}
                    authorAssociation
                    closed
                    closedAt
                    createdAt
                    state
                    updatedAt
                    commits(first: $first_commits) {
                        totalCount
                        pageInfo {
                            endCursor
                            startCursor
                        }
                        nodes {
                            id
                            commit {
                                oid
                                commitUrl
                                committedDate
                                message
                                committer {name}
                            }
                        }
                    }
                }
            }
        }
        rateLimit {
            limit
            cost
            remaining
            resetAt
        }
    }
"""

STARGAZERS_QUERY = """
    query($owner: String!, $name: String!, $items_per_page: Int!, $page_after: String) {
        repository(owner: $owner, name: $name) {
            name
            owner {id login}
            stargazers(first: $items_per_page, orderBy: {field: STARRED_AT, direction: DESC}, after: $page_after) {
                pageInfo {
                    endCursor
                    startCursor
                }
                edges {
                    starredAt
                    node {
                        login
                        avatarUrl
                        url
                    }
                }
            }
        }
        rateLimit {
            limit
            cost
            remaining
            resetAt
        }
    }
"""

DEPLOYMENTS_QUERY = """
    query($owner: String!, $name: String!, $page_size: Int!, $page_after: String) {
        repository(owner: $owner, name: $name) {
            deployments(first: $page_size, after: $page_after) {
                totalCount
                pageInfo {
                    endCursor
                    startCursor
                }
                nodes {
                    id
                    commit {id oid commitUrl committedDate}
                    environment
                    state
                    task
                    createdAt
                    creator {login avatarUrl url}
                    updatedAt
                    latestStatus {
                        id
                        createdAt
                        updatedAt
                        state
                    }
                }
            }
        }
        rateLimit {
            limit
            cost
            remaining
            resetAt
        }
    }
"""

DEFAULT_BRANCH_COMMITS = """
    query($owner: String!, $name: String!, $page_size: Int!, $page_after: String) {
        repository(owner: $owner, name: $name) {
            defaultBranchRef {
                target {
                    ... on Commit {
                        history(first: $page_size, after: $page_after) {
                            totalCount
                            pageInfo {
                                endCursor
                                startCursor
                            }
                            edges {
                                node {
                                    ... on Commit {
                                        id
                                        oid
                                        message
                                        committedDate
                                        commitUrl
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        rateLimit {
            limit
            cost
            remaining
            resetAt
        }
    }
"""

REPOSITORIES = """
    query($owner: String!, $page_size: Int!, $page_after: String) {
        organization(login: $owner) {
            id
            login
            name
            repositories(first: $page_size, after: $page_after) {
                totalCount
                pageInfo {
                    endCursor
                    startCursor
                }
                nodes{
                    id
                    name
                    url
                    isArchived
                }
            }
        }
        rateLimit {
            limit
            cost
            remaining
            resetAt
        }
    }
"""
