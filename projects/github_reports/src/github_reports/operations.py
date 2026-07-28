# This is dirty and gross, but works. Will refactor later (maybe)

# python -m projects.github_reports.src.github_reports.operations
from __future__ import annotations

import argparse
import logging
import pathlib
import shlex
import subprocess
import textwrap
from collections.abc import Callable, Generator, Iterable, Sequence
from typing import Any

import duckdb

HERE = pathlib.Path(__file__).parent
DATA = HERE / "data"
GIT_REMOTE_NAME = "origin"
DRY_RUN = False

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
BLUE = "\033[0;34m"
MAGENTA = "\033[0;35m"
CYAN = "\033[0;36m"
GREY = "\033[38;5;240m"
BOLD = "\033[1m"
RESET = "\033[0m"

logger = logging.getLogger(__file__)
logging.basicConfig(
    level=logging.INFO,
    format=f"{GREY}%(asctime)s{RESET}  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def colour(text: str, colour_: str) -> str:
    return f"{colour_}{text}{RESET}"


def _log(
    log: Callable[[str], None],
    text: str,
    prefix: str,
    colour_: str | None = None,
) -> None:
    for line in text.split("\n"):
        if colour_:
            log(colour(textwrap.indent(line, prefix=prefix), colour_))
        else:
            log(textwrap.indent(line, prefix=prefix))


def _debug(text: str, prefix: str = "") -> None:
    _log(logger.debug, text, prefix, GREY)


def _info(text: str, prefix: str = "") -> None:
    _log(logger.info, text, prefix)


def _warning(text: str, prefix: str = "") -> None:
    _log(logger.warning, text, prefix, YELLOW)


def _error(text: str, prefix: str = "") -> None:
    _log(logger.error, text, prefix, RED)


def _run_git_cmd(args: Iterable[str]) -> Generator[str]:
    cmd = ("git", *args)
    _debug(colour(shlex.join(cmd), BOLD))

    if DRY_RUN:
        return

    # https://stackoverflow.com/a/4417735
    popen = subprocess.Popen(
        args=cmd,
        stdout=subprocess.PIPE,
        universal_newlines=True,
    )
    if popen.stdout:
        for line in popen.stdout:
            yield line.rstrip("\n")
    if popen.stderr:
        for line in popen.stderr:
            yield line.rstrip("\n")

    popen.wait()
    if popen.returncode != 0:
        raise RuntimeError("git returned a non-zero exit code")


def _git(args: Iterable[str]) -> str:
    return "\n".join(_run_git_cmd(args=args))


def _run_report(
    connection: duckdb.DuckDBPyConnection,
    branches_file: pathlib.Path,
    pull_requests_file: pathlib.Path,
) -> Any:
    report_sql = (HERE / "report.sql").read_text(encoding="utf-8")
    replacements = {
        "{{ branches_file }}": str(branches_file),
        "{{ pull_requests_file }}": str(pull_requests_file),
    }
    for placeholder, value in replacements.items():
        report_sql = report_sql.replace(placeholder, value)

    return connection.sql(report_sql)


def branches(args: argparse.Namespace) -> int:
    if args.delete:
        _git(("fetch",))
        full_repo_name = f"{args.organisation}/{args.repository}"
        _info(f"deleting merged branches in {colour(full_repo_name, BOLD)}...")
        conn = duckdb.connect()
        data_path = DATA / args.organisation / args.repository
        if not data_path.exists():
            _error(colour("error: required data does not exist yet", BOLD))
            _error(f"try running `gh-report repo {full_repo_name}` first")
            return 1
        _run_report(
            connection=conn,
            branches_file=data_path / "repository-branches.json",
            pull_requests_file=data_path / "repository-pull-requests.json",
        )
        exclude = args.exclude if args.exclude is not None else []
        exclude_csv = ", ".join(f"'{branch}'" for branch in (exclude or [""]))
        sql = textwrap.dedent(
            f"""
            select branch_name, pr_number, pr_updated_at
            from branch_pr_status
            where 1=1
                and pr_state is not distinct from 'MERGED'
                and branch_name not in ({exclude_csv})
            order by pr_updated_at
            """  # noqa: S608
        )
        _debug("running the following SQL:")
        _debug(sql, prefix="    ")
        for branch_name, pr_number, pr_updated_at in conn.sql(sql).fetchall():
            assert branch_name not in exclude  # noqa: S101
            _info(
                f"deleting {colour(branch_name, BOLD)}"
                + colour(
                    f"  (PR {pr_number} was merged at {pr_updated_at})", GREY
                )
            )
            if args.force:
                _debug(_git(("push", GIT_REMOTE_NAME, "--delete", branch_name)))
                continue

            while True:
                confirm = (
                    input(
                        f"Are you sure you want to delete {colour(branch_name, BOLD)}? [Y/n] "
                    )
                    or "y"
                ).lower()
                if confirm not in ["y", "n"]:
                    _error(f"error: input {confirm!r} not recognised")
                    continue
                else:
                    break
            if confirm == "y":
                _debug(_git(("push", GIT_REMOTE_NAME, "--delete", branch_name)))
            elif confirm == "n":
                _debug(f"skipping {branch_name}")
                continue
            else:
                raise RuntimeError("error: branch should be unreachable")
        _debug(_git(("fetch", "--prune")))
        return 0
    return 1


def main(argv: Sequence[str] | None = None) -> int:
    """
    Parse the arguments and run the command.
    """

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    parser.add_argument(
        "--organisation",
        required=True,
    )
    parser.add_argument(
        "--repository",
        required=True,
    )
    parser.add_argument(
        *("-v", "--verbose"),
        action="count",
        default=0,
    )
    parser.add_argument(
        *("-q", "--quiet"),
        action="count",
        default=0,
    )

    parser__branches = subparsers.add_parser("branches")
    parser__branches.add_argument(
        "--delete",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    parser__branches.add_argument(
        "--exclude",
        action="append",
    )
    parser__branches.add_argument(
        "--force",
        action=argparse.BooleanOptionalAction,
        default=False,
    )

    args = parser.parse_args(argv)
    verbosity = args.verbose - args.quiet
    if verbosity >= 1:
        logger.setLevel(logging.DEBUG)
    if verbosity <= -1:
        logger.setLevel(logging.WARNING)

    if args.command == "branches":
        return branches(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())  # pragma: no cover
