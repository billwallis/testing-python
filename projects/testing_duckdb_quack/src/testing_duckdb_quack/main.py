"""
Inspired by:

https://github.com/mattmartin14/dream_machine/blob/main/duckdb/go_lang/quack_attack/main.go
"""

import asyncio
import dataclasses
import pathlib
from typing import Any

import duckdb

HERE = pathlib.Path(__file__).parent
DUCKDB_HOST = "localhost"
DUCKDB_PASSWORD = "P4$$word"  # noqa: S105


@dataclasses.dataclass
class Client:
    id: str
    conn: duckdb.DuckDBPyConnection

    def sql(self, *args: Any, **kwargs: Any) -> duckdb.DuckDBPyRelation:
        return self.conn.sql(*args, **kwargs)


async def main() -> int:
    server = duckdb.connect(HERE / "server.duckdb")
    clients: list[Client] = [
        Client(id=f"client_{i}", conn=duckdb.connect(":memory:"))
        for i in range(10)
    ]

    # Verify version
    print(duckdb.sql("select version()").fetchone()[0])  # type: ignore

    # Install Quack
    _install_sql = "install quack from core_nightly; load quack;"
    server.sql(_install_sql)
    [client.sql(_install_sql) for client in clients]

    # Create secrets
    _secret_sql = (
        f"create or replace secret (type quack, token '{DUCKDB_PASSWORD}');"
    )
    server.sql(_secret_sql)
    [client.sql(_secret_sql) for client in clients]

    # Start server
    server.sql(
        f"""
        create or replace table logs (
            log_ts timestamp,
            client_id text,
            log_data text
        );
        call quack_serve('quack:{DUCKDB_HOST}', token='{DUCKDB_PASSWORD}');
        """
    )

    # Attach server in clients
    _attach_sql = f"attach 'quack:{DUCKDB_HOST}' as server;"
    [client.sql(_attach_sql) for client in clients]

    # Add some data
    def _insert(
        client: Client,
        content: str,
    ) -> None:
        _insert_sql = """
            insert into server.logs (log_ts, client_id, log_data)
            values (current_timestamp, '{client_id}', '{content}')
        """
        client.sql(_insert_sql.format(client_id=client.id, content=content))

    async with asyncio.TaskGroup() as tg:
        [
            tg.create_task(
                asyncio.to_thread(_insert, client, f"doing iteration {i}")
            )
            for i in range(5)
            for client in clients
        ]

    # Print the added data
    _show_sql = """
        select * replace (strftime(log_ts, '%Y-%m-%d %H:%M:%S.%f') as log_ts)
        from logs
        order by logs.log_ts
    """
    server.sql(_show_sql).show(max_rows=int(1e6), null_value="")

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
