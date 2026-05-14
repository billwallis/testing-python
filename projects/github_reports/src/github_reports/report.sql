create or replace table branches as
    select
        name as branch_name,
        target.oid as commit_sha,
        current_timestamp as updated_at,  /* Should get this from the API */
    from read_json('{{ branches_file }}', union_by_name=True)
;
create or replace table pull_requests as
    select
        number,
        title,
        headRefName as branch_name,
        headRefOid as commit_sha,
        createdAt as created_at,
        mergedAt as merged_at,
        updatedAt as updated_at,
        state,
        -- baseRefName,  /* almost always the `main` branch */
        url,
    from read_json('{{ pull_requests_file }}', union_by_name=True)
    order by number
;
create or replace table branch_pr_status as
    select
        commit_sha,
        branches.branch_name,
        pull_requests.number as pr_number,
        pull_requests.updated_at as pr_updated_at,
        pull_requests.state as pr_state,
    from branches
        asof left join pull_requests
            using (commit_sha, updated_at)
    order by
        if(branches.branch_name = 'main', 0, 1),
        pr_updated_at desc
;
/* Report */
select
    coalesce(pr_state, 'NO PR') as pr_state,
    count(*) as branch_count,
from branch_pr_status
group by pr_state
order by pr_state
;
