{% macro safe_growth_rate(current_value, previous_value) %}

CASE
    WHEN {{ previous_value }} = 0 THEN NULL
    ELSE (
        (
            {{ current_value }} - {{ previous_value }}
        )::FLOAT
        /
        {{ previous_value }}
    )
END

{% endmacro %}