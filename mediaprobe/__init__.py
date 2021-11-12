"""
A straightforward wrapper for the Mediainfo CLI tool. It calls mediainfo as a subprocess and parses the returning
JSON into formatted datatypes relevent to the function called.
"""

import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    here = Path(sys._MEIPASS)
else:
    here = Path(__file__).parent

if sys.platform == "win32":
    mibin = str(here / "bin" / "mediainfo.exe")
elif sys.platform == "darwin":
    mibin = str(here / "bin" / "mediainfo")
else:
    raise RuntimeError(f"Platform not supported: {sys.platform}")

from .mediaprobe import * # type: ignore