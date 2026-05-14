import glob
import pathlib

import sqlglot

HERE = pathlib.Path(__file__).parent


def migrate_scripts(sql_dir: pathlib.Path) -> None:
    """
    Migrate SQL scripts from T-SQL to PostgreSQL using SQLGlot.
    """

    from_dialect, to_dialect = "tsql", "postgres"
    paths = glob.glob(f"{sql_dir}/**/*.sql", recursive=True)
    for path in paths:
        file = sql_dir / path
        content = file.read_text(encoding="utf-8")
        migrated = sqlglot.transpile(
            content,
            read=from_dialect,
            write=to_dialect,
            pretty=True,
        )
        file.write_text(";\n\n".join(migrated))


def main() -> None:
    migrate_scripts(HERE / "models")


if __name__ == "__main__":
    main()
