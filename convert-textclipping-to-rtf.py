#!/usr/bin/python3

import plistlib
import sys
from pathlib import Path

def convert(clippath: Path):
    with clippath.open('rb') as fi:
        plist = plistlib.load(fi)
        rtf = plist['UTI-Data']['public.rtf']

        with clippath.with_suffix(".rtf").open(mode='w', encoding='utf-8') as ft:
            ft.write(rtf)
    clippath.unlink()

for path in sys.argv[1:]:
    convert(Path(path))
