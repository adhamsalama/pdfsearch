#! /usr/bin/python

from typing import Pattern
import typer
import pdftotext
import re
from concurrent.futures import Future, ProcessPoolExecutor, wait

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


def search_pdf(
    filename: str,
    start: int,
    end: int,
    regex: Pattern[str],
    regex_list: list[str],
    plain: bool,
):
    with open(filename, "rb") as file:
        pdf = pdftotext.PDF(file)
        matches: list[str] = []
        for i in range(start, end):
            page = pdf[i]
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
    return matches


@app.command()
def search(
    filename: str,
    query: list[str],
    ignorecase: bool = typer.Option(True, help="Ignore case for searching"),
    exact: bool = typer.Option(False, help="Match exact substring"),
    plain: bool = typer.Option(
        False, help="Output plaintext without coloring, bolding and underlining"
    ),
    processes: int = typer.Option(1, help="Number of parallel processes"),
):
    with open(filename, "rb") as file:
        pdf = pdftotext.PDF(file)
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
        with ProcessPoolExecutor(processes) as executor:
            searches: list[Future[list[str]]] = []
            step = len(pdf) // processes
            step = step if step > 0 else 1
            for i in range(0, len(pdf), step):
                next_index = i + len(pdf) // processes
                next_index = next_index if 0 < next_index < len(pdf) else len(pdf)
                searches.append(
                    executor.submit(
                        search_pdf,
                        filename=filename,
                        start=i,
                        end=next_index,
                        regex=regex,
                        regex_list=regex_list,
                        plain=plain,
                    )
                )
            wait(searches)
            for search in searches:
                for result in search.result():
                    print(result)


if __name__ == "__main__":
    app()
