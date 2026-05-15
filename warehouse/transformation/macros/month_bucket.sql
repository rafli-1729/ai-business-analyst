{% macro month_bucket(column_name) %}

DATE_TRUNC(
    'month',
    {{ column_name }}
)

{% endmacro %}