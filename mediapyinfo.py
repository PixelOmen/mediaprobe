import json
import pathlib
import subprocess as sub
from sys import platform

testfile = pathlib.Path("D:", "/CodingProjects", "_ffmpeg", "resolve_OG.mov")

def init():
    global mibin

    if platform == "win32":
        mibin = pathlib.Path("./bin/mediainfo.exe")

def getall(filepath):
    try:
        mibin
    except NameError:
        init()
    miproc = sub.Popen(f"{str(mibin)} {filepath} --output=JSON", stdin=sub.PIPE, stdout=sub.PIPE, stderr=sub.PIPE)
    fileoutput = json.loads(miproc.stdout.read())['media']['track']
    return fileoutput


jsonresult = getall(str(testfile))

for key in jsonresult[0]:
    print(key)
    
