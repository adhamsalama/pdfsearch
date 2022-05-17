#! /usr/bin/python
from typing import cast, Any
import typer
import pdftotext  # type: ignore
import re

app = typer.Typer()


class Color:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


@app.command()
def search(
    filename: str,
    query: list[str],
    ignorecase: bool = typer.Option(True, help="Ignore case for searching"),
    exact: bool = typer.Option(False, help="Match exact substring"),
    plain: bool = typer.Option(
        False, help="Output plaintext without coloring, bolding and underlining"
    ),
):
    with open(filename, "rb") as file:
        pdf = pdftotext.PDF(file)
        results: list[Any] = []
        regex_list: list[str] = []
        for word in query:
            regex_list.append(re.escape(word))
        if exact:
            regex_pattern = "(" + "|".join(regex_list) + ")"
        else:
            regex_pattern = ".*(?:" + "|".join(regex_list) + ").*"
        if ignorecase:
            regex = re.compile(regex_pattern, re.IGNORECASE)
        else:
            regex = re.compile(regex_pattern)
        matches: list[str] = []
        for page in pdf:
            # find matches
            for x in regex.findall(page):
                if not plain:
                    # color matches
                    colored = x
                    matches_to_color = re.compile(
                        "(" + "|".join(regex_list) + ")", re.IGNORECASE
                    ).findall(x)
                    for m in matches_to_color:
                        colored = colored.replace(
                            m,
                            Color.GREEN + Color.BOLD + Color.UNDERLINE + m + Color.END,
                        )
                    matches.append(colored)
                else:
                    matches.append(x)
        for result in matches:
            print(result)


if __name__ == "__main__":
    app()
