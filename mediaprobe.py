"""
A straightforward wrapper for the Mediainfo CLI tool. It calls mediainfo as a subprocess and parses the returning
JSON into formatted datatypes relevent to the function called.
"""

import json
import pathlib
import subprocess as sub
from sys import platform

testfile = pathlib.Path('c:', '/Mount', 'rei08', 'DCI', 'testing', '_Testfiles', 'Logan_8Ch.mov')

def _init():
    global mibin

    if platform == "win32":
        mibin = pathlib.Path("./bin/mediainfo.exe")
    else:
        raise EnvironmentError("This library is currently only compatible with Windows")

def all(filepath, raw=False):
    """
    Returns a dictionary with 2 keys: 'path' and 'tracks'. 'path' is the original path
    that was passed into this function. 'tracks' contains a list of tracks where each
    track is a dictionary that contains properties for that track.

    Setting 'raw' to 'True' will return the unchanged JSON output(as bytes) straight from the Mediainfo CLI.
    """
    if not pathlib.Path(filepath).is_file():
        raise FileNotFoundError(f"'{filepath}' is not a path to a file or does not exist")
    try:
        mibin
    except NameError:
        _init()
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

def audio(filepath, tracks=False):
    """
    Returns the total number of audio channels as an int. 

    If 'tracks=True', it instead returns a list of tuples.
    The tuples contain the index of the stream and the number of channels in that stream.
    """
    output = all(filepath)
    
    chspertrack = []
    trackorder = []

    for track in output['tracks']:
        if track["@type"] == 'Audio':
            chspertrack.append(track['Channels'])
            trackorder.append(track['StreamOrder'])

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