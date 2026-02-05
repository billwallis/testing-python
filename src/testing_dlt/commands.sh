cd src/testing_dlt/

uv run jira_pipeline.py
#dlt pipeline jira_pipeline show
duckdb jira_pipeline.duckdb -ui
duckdb jira_search_pipeline.duckdb -ui

uv run jira_rest_api_pipeline.py
duckdb jira_rest_api_pipeline.duckdb -ui
