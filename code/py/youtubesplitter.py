"""
youtubesplitter.py
2021 Szieberth Ádám - Public Domain

This script splits a downloaded YouTube media file by its chapters.

Usage:
python youtubesplitter.py <myyoutubemediafile>

Hint: call youtube-dl with the `--write-info-json` option previously.

Notes:
* If you have the media file downloaded already you can prevent its re-download
  with the `--skip-download` youtube-dl option.

* FFmpeg executable is assumed to be in your %PATH%.
"""

import json
import os
import pathlib
import re
import sys

filename_replaces = {
    "<":  "_lessthan_",
    ">":  "_greaterthan_",
    ":":  "_colon_",
    '"':  "_doublequote_",
    "/":  "_forthslash_",
    "\\": "_backslash_",
    "|":  "_bar_",
    "?":  "_questionmark_",
    "*":  "_star_",
}

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print(f'ERROR! Path of media file is assumed as first argument.')
        print(__doc__)
        sys.exit(1)

    p = pathlib.Path(sys.argv[1]).resolve()

    if not p.is_file():
        print(f'ERROR! Incorrect path.')
        print(__doc__)
        sys.exit(2)

    pext = p.suffix.lstrip(".")

    pj = p.parent / f'{p.stem}.info.json'

    if not pj.is_file():
        print(f'ERROR! Missing Info JSON.\nExpected the following file: "{pj}"')
        print(__doc__)
        sys.exit(3)

    with pj.open("r", encoding="utf-8") as f:
        info = json.load(f)

    chapters = info.get("chapters", [])

    for nr, c in enumerate(chapters, 1):
        title = c["title"]
        nrm = re.search('^\d+\.?\s+', title)
        if nrm:
            nrstr = nrm.group(0).rstrip()
            nr = int(nrstr.rstrip("."))
            title = title[nrm.end():]
        else:
            nrstr = f'{nr}.'
        po = pathlib.Path("".join(filename_replaces.get(c, c) for c in f'{nr:0>2} {title}.{pext}'))
        command = f'ffmpeg -i "{p}" -ss {c["start_time"]} -to {c["end_time"]} -c copy "{po}"'
        print("\n" * (1 if 1<nr else 0) + command, end="\n\n")
        os.system(command)
