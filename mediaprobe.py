import json
import pathlib
import subprocess as sub
from sys import platform

testfilehome = pathlib.Path("D:", "/CodingProjects", "_ffmpeg", "resolve_OG.mov")
testfile = pathlib.Path('c:', '/Mount', 'rei08', 'DCI', 'testing', '_Testfiles', 'Logan_8Ch.mov')

def _init():
    global mibin

    if platform == "win32":
        mibin = pathlib.Path("./bin/mediainfo.exe")

def getall(filepath):
    if not pathlib.Path(filepath).is_file():
        raise TypeError(f"'{filepath}' is not a path to a file or does not exist")
    try:
        mibin
    except NameError:
        _init()
    miproc = sub.Popen(f"{str(mibin)} {filepath} --output=JSON", stdin=sub.PIPE, stdout=sub.PIPE, stderr=sub.PIPE)
    fileoutput = json.loads(miproc.stdout.read())['media']

    path = fileoutput['@ref']
    del fileoutput['@ref']
    fileoutput['path'] = path

    tracks = fileoutput['track']
    del fileoutput['track']
    fileoutput['tracks'] = tracks

    return fileoutput

def getaudio(filepath, tracks=False):
    output = getall(filepath)
    
    chspertrack = []
    trackorder = []

    for track in output['tracks']:
        if track["@type"] == 'Audio':
            chspertrack.append(track['Channels'])
            trackorder.append(track['StreamOrder'])

    if tracks:
        return [x for x in zip(trackorder, chspertrack)]
    else:
        totalchs = 0
        for ch in chspertrack:
            totalchs += int(ch)
        return totalchs
    
def getfps(filepath):
    output = getall(filepath)

    for track in output['tracks']:
        if track['@type'] == "Video":
            return track['FrameRate']

