from pathlib import Path
import sys

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

from .mediaprobe import *