"""
https://rich.readthedocs.io/en/latest/introduction.html
"""

from rich.console import Console

console = Console()


def main() -> None:
    # print("Hello, World!")
    # rich.print("[blue]Hello, [yellow bold]World!")

    console.render("Hello, [bold magenta]Rich[/bold magenta] World!")
    console.print("Hello, [bold magenta]Rich[/bold magenta] World!")


if __name__ == "__main__":
    main()
