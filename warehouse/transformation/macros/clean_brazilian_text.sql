{% macro clean_brazilian_text(column_name) %}
    INITCAP(
        TRIM(
            TRANSLATE(
                LOWER(
                    SPLIT_PART(
                        SPLIT_PART({{ column_name }}::TEXT, '-', 1), 
                        '(', 1
                    )
                ),
                'áàâãéêíóôõúç',
                'aaaaeeiooouc'
            )
        )
    )
{% endmacro %}
