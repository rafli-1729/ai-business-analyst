import pytest

from core_analytics.analytics.sql_guard import SqlValidationError, validate_sql_is_read_only


def test_validate_sql_allows_single_select_statement():
    sql = validate_sql_is_read_only("select * from gold.sales_summary limit 10;")

    assert sql == "select * from gold.sales_summary limit 10"


def test_validate_sql_blocks_mutating_statements():
    with pytest.raises(SqlValidationError):
        validate_sql_is_read_only("delete from gold.sales_summary")


def test_validate_sql_blocks_multiple_statements():
    with pytest.raises(SqlValidationError):
        validate_sql_is_read_only("select 1; select 2;")


def test_validate_sql_extracts_markdown_fenced_sql():
    sql = validate_sql_is_read_only(
        """
        Here is the query:

        ```sql
        SELECT customer_state, AVG(customer_satisfaction_score) AS avg_review_score
        FROM gold.order_item_facts
        GROUP BY customer_state;
        ```
        """
    )

    assert sql.startswith("SELECT customer_state")


def test_validate_sql_extracts_sql_after_prefix():
    sql = validate_sql_is_read_only("SQL: SELECT customer_state FROM gold.state_performance;")

    assert sql == "SELECT customer_state FROM gold.state_performance"


def test_validate_sql_allows_semicolon_inside_string_literal():
    sql = validate_sql_is_read_only("select 'a;b' as label;")

    assert sql == "select 'a;b' as label"


def test_validate_sql_does_not_extract_select_from_prose():
    with pytest.raises(SqlValidationError):
        validate_sql_is_read_only("I will select the best states with this query.")
