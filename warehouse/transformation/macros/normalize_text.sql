{% macro normalize_text(column_name) %}

LOWER(
    TRIM(
        {{ column_name }}
    )
)

{% endmacro %}