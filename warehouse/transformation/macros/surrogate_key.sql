{% macro surrogate_key(columns) %}

md5(
    concat(
        {% for col in columns %}
            coalesce({{ col }}::TEXT, '')
            {% if not loop.last %}, '|' ,{% endif %}
        {% endfor %}
    )
)

{% endmacro %}