"""
A straightforward wrapper for the Mediainfo CLI tool. It calls mediainfo as a subprocess and parses the returning
JSON into formatted datatypes relevent to the function called.
"""

import sys
import json
import subprocess as sub
from pathlib import Path
from typing import Union
from enum import Enum

# testfile constant and binary path initialization
testfile = r"\\10.0.20.175\rei08\DCI\testing\_Testfiles\Logan_8Ch.mov"

if __name__ == "__main__":
    if sys.platform == "win32":
        mibin = str(Path(__file__).parent / "bin" / "mediainfo.exe")
        useshell = False
    elif sys.platform == "darwin":
        mibin = str(Path(__file__).parent / "bin" / "mediainfo")
        useshell = True
    else:
        raise RuntimeError(f"Platform not supported: {sys.platform}")
else:
    from . import mibin , useshell

class tracktypes(Enum):
    general = "General"
    video = "Video"
    audio = "Audio"
    image = "Image"
    data = "Data"
    other = "Other"

def get_tracktype(trk_type: str) -> tracktypes:
    return tracktypes(trk_type.lower().capitalize())

def all(filepath: Union[str, Path], raw: bool=False) -> Union[dict, bytes, None]:
    """
    Returns a dictionary with 2 keys: 'path' and 'tracks'. 'path' is the original path
    that was passed into this function. 'tracks' contains a list of tracks where each
    track is a dictionary that contains properties for that track. Returns None if it
    is unable to get/parse the JSON output.

    Setting 'raw' to 'True' will return the unchanged JSON output(as bytes) straight from the Mediainfo CLI.
    """
    if not Path(filepath).is_file():
        raise FileNotFoundError(f"'{filepath}' is not a path to a file or does not exist")

    if " " in str(filepath):
        filepath = f'"{str(filepath)}"'

    miproc = sub.Popen(f"{str(mibin)} {filepath} --output=JSON", stdin=sub.PIPE, stdout=sub.PIPE, stderr=sub.PIPE, shell=useshell)
    rawbytes = miproc.stdout.read()
    if raw:
        return rawbytes

    rawstr = rawbytes.decode('utf-8')
    try:
        fileoutput = json.loads(rawstr)
    except json.JSONDecodeError as e:
        print(e)
        return None

    if fileoutput == None:
        return None

    fileoutput = fileoutput['media']

    path = fileoutput['@ref']
    del fileoutput['@ref']
    fileoutput['path'] = path

    tracks = fileoutput['track']
    del fileoutput['track']
    fileoutput['tracks'] = tracks

    return dict(fileoutput)

def audio(filepath: Union[str, Path], tracks: bool=False, pids: bool=False) -> Union[int, list, None]:
    """
    Returns the total number of audio channels as an int.

    If 'tracks=True', it instead returns a list of tuples.
    The tuples contain the index of the stream and the number of channels in that stream.
    If 'pids=True', it returns the pids in the first pos of the tuple instead of the stream order.
    """
    output = all(filepath)
    if not output:
        return None

    chspertrack = []
    trackorder = []

    if pids:
        datafield = 'ID'
    else:
        datafield = 'StreamOrder'

    for track in output['tracks']:
        if track["@type"] == 'Audio':
            chspertrack.append(track['Channels'])
            trackorder.append(track[datafield])

    if not chspertrack and not trackorder:
        return None

    if tracks:
        return list([x for x in zip(trackorder, chspertrack)])
    else:
        totalchs = 0
        for ch in chspertrack:
            totalchs += int(ch)
        return int(totalchs)

def fps(filepath: Union[str, Path]) -> Union[str, None]:
    output = all(filepath)
    if not output:
        return None

    for track in output['tracks']:
        if track['@type'] == "Video":
            return track.get('FrameRate', None)

def streamtypes(filepath: Union[str, Path]) -> Union[list, None]:
    """
    Returns a list that contains types for each stream, in order.
    """
    output = all(filepath)
    if not output:
        return None

    alltypes = []
    order = []

    for track in output['tracks']:
        if track['@type'] != 'General':
            alltypes.append(track['@type'])
            order.append(track['StreamOrder'])

    tosort = [x for x in zip(alltypes, order)]
    tosort.sort(key= lambda x:x[1])
    sorted = [x[0] for x in tosort]

    return sorted

def duration(filepath: Union[str, Path], frames: bool=True) -> Union[str, None]:
    """
    Returns the total duration in frames. If frames=False, returns the
    starting TC instead (if available).
    """
    output = all(filepath)
    if not output:
        return None

    if frames:
        for track in output['tracks']:
            if track['@type'] == "Video":
                return track.get('FrameCount', None)
    else:
        for track in output['tracks']:
            if track['@type'] == "Other":
                return track.get('TimeCode_FirstFrame', None)

    return None

def colorspace(filepath: Union[str, Path]) -> Union[str, None]:
    output = all(filepath)
    if not output:
        return None
    for track in output['tracks']:
        if track['@type'] == 'Video':
            try:
                found = track['ColorSpace']
            except KeyError:
                return None
            else:
                return found
    for track in output['tracks']:
        if track['@type'] == 'Image':
            try:
                found = track['ColorSpace']
            except KeyError:
                return None
            else:
                return found

def search(filepath: Union[str, Path], searchterm: str, tracktype: Union[str, tracktypes]) -> Union[str, None]:
    if isinstance(tracktype, str):
        try:
            tracktype = get_tracktype(tracktype)
        except ValueError:
            print((f"Invalid tracktype: {tracktype}"))
            return None

    output = all(filepath)
    if not output:
        return None

    for track in output['tracks']:
        if track['@type'] == tracktype.value:
            return track.get(searchterm, None)


if __name__ == "__main__":
    print(search(testfile, "Format_Profile", "vIdEo"))
