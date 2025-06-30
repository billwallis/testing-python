create or replace table branches as
    select
        name as branch_name,
        commit.sha as commit_sha,
        current_timestamp as updated_at,  /* Should get this from the API */
    from read_json('{{ branches_file }}', union_by_name=True)
;
create or replace table pull_requests as
    select
        number,
        title,
        head.ref as branch_name,
        head.sha as commit_sha,
        created_at,
        updated_at,
        case
            when state = 'open'        then 'open'
            when merged_at is not null then 'merged'
            when closed_at is not null then 'closed'
                                       else 'unknown'
        end as status,
        head,
        -- base,  /* almost always the `main` branch */
        html_url as url,
    from read_json('{{ pull_requests_file }}', union_by_name=True)
    order by number
;
create or replace table branch_pr_status as
    select
        commit_sha,
        branches.branch_name,
        pull_requests.number as pr_number,
        pull_requests.updated_at as pr_updated_at,
        pull_requests.status as pr_status,
    from branches
        asof left join pull_requests
            using (commit_sha, updated_at)
    order by
        if(branches.branch_name = 'main', 0, 1),
        pr_updated_at desc
;
/* Report */
select
    coalesce(pr_status, 'no pr') as pr_status,
    count(*) as branch_count,
from branch_pr_status
group by pr_status
order by pr_status
;
