cd src/testing_dlt/

uv run jira_pipeline.py
uv run jira_rest_api_pipeline.py
uv run github_pipeline.py


###
duckdb -ui
attach '<destination>.duckdb'


duckdb github_tasman_analytics.duckdb -ui
