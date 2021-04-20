"""
syntax_py.py
2021 Szieberth Ádám - Public Domain

This script does the Python code syntax highlighting for Szieberth Ádám's
personal webpage. As all the text content there are rendered with a monospaced
font and are centered, all lines should have the same width to assure alignment.

The script does the syntax highlighting and it also adds the necessary number of
spaces to the end of each line.
"""

try:
    import pygments
except ImportError:
    pygments = None
else:
    import pygments.lexers
    import pygments.formatters

import pathlib
import sys

usage = """
Usage:

python syntax_py.py [margin] <mypyfile>

Output goes to "<mypyfile>.html".

Notes:

* `pygments` Python module must be installed."""

if __name__ == "__main__":

    if pygments is None:
        print(f'ERROR! Third party module `pygments` is missing.')
        print(f'Hint: You can install it by calling `pip install pygments`.')
        print(f'{__doc__}{usage}')
        sys.exit(1)

    if len(sys.argv) < 2:
        print(f'ERROR! Path of a python file is assumed as last argument.')
        print(f'{__doc__}{usage}')
        sys.exit(2)

    margin = None
    if 2 < len(sys.argv):
        if sys.argv[1].isdecimal():
            margin = int(sys.argv[1])
        else:
            print(f'ERROR! Integer margin size is assumed as first argument.')
            print(f'{__doc__}{usage}')
            sys.exit(3)

    p = pathlib.Path(sys.argv[-1]).resolve()
    pext = p.suffix.strip(".")

    with p.open("r", encoding="utf-8") as f:
        code = f.read()

    highlighted = pygments.highlight(code, pygments.lexers.PythonLexer(), pygments.formatters.HtmlFormatter())

    codelinelens = [len(s) for s in code.split("\n")]
    maxcodelinelens = max(codelinelens)
    margin = margin or maxcodelinelens
    if margin < maxcodelinelens :
        print("ERROR! Too low margin size!")
        print(f'Hint: Its minimum is the highest column number which is {maxcodelinelens}.')
        print(f'{__doc__}{usage}')
        sys.exit(4)
    highlightedlinse = highlighted.split("\n")
    result = "\n".join(s + (" "*(margin-w) if w else "") for s, w in zip(highlightedlinse, codelinelens))

    po = p.parent / f'{p.stem}.{pext}.html'

    with po.open("w", encoding="utf-8") as f:
        f.write(result)
