"""
A straightforward wrapper for the Mediainfo CLI tool. It calls mediainfo as a subprocess and parses the returning
JSON into formatted datatypes relevent to the function called.
"""

import json
import subprocess as sub
import sys
from pathlib import Path

testfile = r"\\10.0.20.175\rei08\DCI\testing\_Testfiles\Logan_8Ch.mov"

if getattr(sys, 'frozen', False):
    binpath = Path(sys._MEIPASS) / 'bin'
else:
    binpath = Path(__file__).parent / 'bin'

if sys.platform == "win32":
    mibin = str(binpath / 'mediainfo.exe')
elif sys.platform == "darwin":
    mibin = str(binpath / 'mediainfo')
else:
    raise EnvironmentError("This library is currently only compatible with Windows and MacOS")

def all(filepath, raw=False):
    """
    Returns a dictionary with 2 keys: 'path' and 'tracks'. 'path' is the original path
    that was passed into this function. 'tracks' contains a list of tracks where each
    track is a dictionary that contains properties for that track.

    Setting 'raw' to 'True' will return the unchanged JSON output(as bytes) straight from the Mediainfo CLI.
    """
    if not Path(filepath).is_file():
        raise FileNotFoundError(f"'{filepath}' is not a path to a file or does not exist")

    if " " in str(filepath):
        filepath = f'"{str(filepath)}"'

    miproc = sub.Popen(f"{str(mibin)} {filepath} --output=JSON", stdin=sub.PIPE, stdout=sub.PIPE, stderr=sub.PIPE)
    rawbytes = miproc.stdout.read()
    rawstr = rawbytes.decode('utf-8')
    fileoutput = json.loads(rawstr)

    if raw:
        return rawbytes

    fileoutput = fileoutput['media']

    path = fileoutput['@ref']
    del fileoutput['@ref']
    fileoutput['path'] = path

    tracks = fileoutput['track']
    del fileoutput['track']
    fileoutput['tracks'] = tracks


    return dict(fileoutput)

def audio(filepath, tracks=False, pids=False):
    """
    Returns the total number of audio channels as an int. 

    If 'tracks=True', it instead returns a list of tuples.
    The tuples contain the index of the stream and the number of channels in that stream.
    If 'pids=True', it returns the pids in the first pos of the tuple instead of the stream order.
    """
    output = all(filepath)
    
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

    if tracks:
        return list([x for x in zip(trackorder, chspertrack)])
    else:
        totalchs = 0
        for ch in chspertrack:
            totalchs += int(ch)
        return int(totalchs)
    
def fps(filepath):
    output = all(filepath)

    for track in output['tracks']:
        if track['@type'] == "Video":
            return str(track['FrameRate'])

def streamtypes(filepath):
    """
    Returns a list that contains types for each stream, in order.
    """
    output = all(filepath)

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

def duration(filepath, frames=True):
    output = all(filepath)

    for track in output['tracks']:
        if track['@type'] == "Video":
            if frames:
                return str(track['FrameCount'])
            else:
                return str(track['Duration'])
    return None

def colorspace(filepath):
    output = all(filepath)
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

def search(filepath, searchterm, tracktype):
    if tracktype.lower() == 'video':
        tracktype = "Video"
    elif tracktype.lower() == "audio":
        tracktype = "Audio"
    elif tracktype.lower() == "image":
        tracktype = "Image"
    else:
        raise ValueError(f"Invalid tracktype: {tracktype}")
    output = all(filepath)

    for track in output['tracks']:
        if track['@type'] == tracktype:
            try:
                found = track[searchterm]
            except KeyError:
                return None
            else:
                return found


if __name__ == "__main__":
    print(fps(testfile))