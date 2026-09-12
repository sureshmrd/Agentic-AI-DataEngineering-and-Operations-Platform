import pytest

from api_server.business_database import validate_sql


def test_valid_select():
    sql = """
        SELECT month, gross_revenue
        FROM monthly_sales_summary
        ORDER BY month
    """

    result = validate_sql(sql)

    assert "LIMIT 100" in result


def test_existing_limit_is_allowed():
    sql = """
        SELECT *
        FROM category_performance
        LIMIT 10
    """

    result = validate_sql(sql)

    assert "LIMIT 10" in result


def test_dml_is_rejected():
    with pytest.raises(ValueError):
        validate_sql(
            "DELETE FROM monthly_sales_summary"
        )


def test_disallowed_table_is_rejected():
    with pytest.raises(ValueError):
        validate_sql(
            "SELECT * FROM orders"
        )


def test_multiple_statements_are_rejected():
    with pytest.raises(ValueError):
        validate_sql(
            "SELECT * FROM monthly_sales_summary; "
            "DROP TABLE monthly_sales_summary;"
        )


def test_empty_sql_is_rejected():
    with pytest.raises(ValueError):
        validate_sql("")