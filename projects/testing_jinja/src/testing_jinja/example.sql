{% set some_columns = ["col_1", "col_2", "col_3", "col_4", "col_5"] %}

select
    {% for column in some_columns -%}
        {{ column }},
    {% endfor %}
    {% for column in some_columns -%}
        cast({{ column }} as int) as {{ column }}_int{% if not loop.last %},{% endif %}
    {% endfor %}
from some_table
