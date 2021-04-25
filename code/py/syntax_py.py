"""
syntax_py.py
2021 Szieberth Ádám - Public Domain

This script does the Python code syntax highlighting for Szieberth Ádám's
personal webpage. As all the text content there are rendered with a monospaced
font and are centered, all lines should have the same width to assure alignment.

The script does the syntax highlighting and it also adds the necessary number of
spaces to the end of each line.

Usage:

python syntax_py.py [textwidth] [nohighlight] <mypyfile>

Output goes to "<mypyfile>.html".

Notes:

* `pygments` Python module must be installed.
"""

try:
    import pygments
except ImportError:
    pygments = None
else:
    from pygments.lexers import PythonLexer
    from pygments.formatters import HtmlFormatter

import pathlib
import sys

if __name__ == "__main__":

    options = {"nohighlight": False}

    if pygments is None:
        print(f'ERROR! Third party module `pygments` is missing.')
        print(f'Hint: You can install it by calling `pip install pygments`.')
        print(__doc__)
        sys.exit(1)

    if len(sys.argv) < 2 or not pathlib.Path(sys.argv[-1]).is_file():
        print(f'ERROR! Path of a (Python) file is assumed as last argument.')
        print(__doc__)
        sys.exit(2)

    textwidth = None
    for s in sys.argv[1:-1]:
        if s.isdecimal():
            textwidth = int(s)
        elif s in options:
            options[s] = True
        else:
            print(f'ERROR! invalid argument: "{s}".')
            print(f'Hint: Expected an integer textwidth or any of the following options:')
            for so in options:
                print(f'      * {so}')
            print(__doc__)
            sys.exit(3)

    p = pathlib.Path(sys.argv[-1]).resolve()
    pext = p.suffix.strip(".")

    with p.open("r", encoding="utf-8") as f:
        a = f.read()

    alinelens = [len(s) for s in a.split("\n")]
    maxalinelens = max(alinelens)
    textwidth = textwidth or maxalinelens
    if textwidth < maxalinelens :
        print("ERROR! Too low textwidth size!")
        print(f'Hint: Its minimum is the highest column number which is {maxalinelens}.')
        print(__doc__)
        sys.exit(4)

    if not options["nohighlight"]:
        a = pygments.highlight(a, PythonLexer(), HtmlFormatter())

    a = a.split("\n")
    result = "\n".join(s + (" "*(textwidth-w) if w else "") for s, w in zip(a, alinelens))

    po = p.parent / f'{p.stem}.{pext}.html'

    with po.open("w", encoding="utf-8") as f:
        f.write(result)
