# /// script
# dependencies = [
#   "duckdb>=1.3.1",
#   "sqlglot[rs]>=27.2.0",
# ]
# ///

import duckdb
import sqlglot
import sqlglot.optimizer.qualify

TableColumns = dict[str, set[str]]

SQL_DIALECT = "duckdb"
VALID_SQL = """
    select
        payments.payment_id,
        payments.amount,
        payments.user_id,
        users.user_name,
        (payments.amount < 0) as is_refund,
    from payments
        left join users
            using (user_id)
"""
INVALID_SQL = """
    select
        customer_id,
        user_id,
        amount,
    from customers
"""


class ObjectNotFoundError(Exception):
    """
    Exception raised when an object is not found.
    """


def create_duckdb_objects() -> None:
    """
    Create the DuckDB objects for testing.
    """

    duckdb.sql(
        """
        create table users (
            user_id integer,
            user_name text,
        );
        create table payments (
            payment_id integer,
            user_id integer,
            amount numeric(12, 2),
        );
        """
    )


def get_information_schema_objects() -> TableColumns:
    """
    Return a dictionary with the tables and columns in the information schema.
    """

    information_schema_objects = {}
    information_schema_sql = """
        select table_name, column_name
        from information_schema.columns
    """
    for row in duckdb.sql(information_schema_sql).fetchall():
        table, column = row
        information_schema_objects.setdefault(table, set()).add(column)

    return information_schema_objects


def get_query_objects(sql_query: str) -> TableColumns:
    """
    Return a dictionary with the source tables and columns in the query.
    """

    sql = sqlglot.optimizer.qualify.qualify(
        sqlglot.parse_one(sql_query, read=SQL_DIALECT)
    )
    query_objects = {
        table.name: set() for table in sql.find_all(sqlglot.expressions.Table)
    }
    for column in sql.find_all(sqlglot.expressions.Column):
        if column.table:  # not a calculated column
            query_objects[column.table].add(column.name)

    return query_objects


def validate_query_objects(
    known_objects: TableColumns,
    query_objects: TableColumns,
) -> None:
    """
    Validate that the query objects exist in the catalogue.
    """

    known_tables = list(known_objects)
    for table, columns in query_objects.items():
        if table not in known_tables:
            raise ObjectNotFoundError(
                f"Table '{table}' not found.\nKnown tables are: {known_tables}"
            )

        known_columns = known_objects[table]
        if not columns.issubset(known_columns):
            raise ObjectNotFoundError(
                f"Some columns selected from table '{table}' do not exist.\n"
                f"Found columns: {columns}\nKnown columns: {known_columns}"
            )


def main() -> None:
    """
    Validate that an "LLM-generated" SQL query is referencing objects which
    exist in the database.
    """

    create_duckdb_objects()
    valid_sql_objects = get_query_objects(VALID_SQL)
    print(valid_sql_objects)
    invalid_sql_objects = get_query_objects(INVALID_SQL)

    # Could also use the dbt manifest file to avoid a DB query
    db_objects = get_information_schema_objects()

    # Passes fine
    validate_query_objects(db_objects, valid_sql_objects)

    # Raises an error
    validate_query_objects(db_objects, invalid_sql_objects)


if __name__ == "__main__":
    main()
