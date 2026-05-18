{% macro apply_geo_mapping(column_name, mapping_type) %}
    {% if mapping_type == 'state' %}
        COALESCE(
            (SELECT state_name FROM {{ ref('state_mapping') }} WHERE state_code = UPPER(TRIM({{ column_name }}))),
            UPPER(TRIM({{ column_name }}))
        )
    {% elif mapping_type == 'city' %}
        COALESCE(
            (SELECT canonical_city FROM {{ ref('city_mapping') }} WHERE raw_city = {{ column_name }}),
            {{ column_name }}
        )
    {% endif %}
{% endmacro %}
