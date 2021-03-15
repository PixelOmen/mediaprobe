"""
A straightforward wrapper for the Mediainfo CLI tool. It calls mediainfo as a subprocess and parses the returning
JSON into formatted datatypes relevent to the function called.
"""

import json
import pathlib
import subprocess as sub
import sys

here = pathlib.Path(__file__).parent.resolve()
platform = sys.platform

if platform == "win32":
    mibin = here / 'bin' / 'mediainfo.exe'
    if not mibin.is_file():
    	mibin = here.parent.resolve() / 'bin' / 'mediainfo.exe'
    if not mibin.is_file():
        raise EnvironmentError("Unable to locate the MediaInfo exe")
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

    miproc = sub.Popen(f"{str(mibin)} {filepath} --output=JSON", stdin=sub.PIPE, stdout=sub.PIPE, stderr=sub.PIPE)
    rawbytes = miproc.stdout.read()
    rawstr = rawbytes.decode('utf-8')
    fileoutput = json.loads(rawstr)

    if raw:
        return rawbytes

    try:
        fileoutput = fileoutput['media']
    except KeyError:
        return False

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

    if not output:
    	return False
    
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

def findaudiostream(filepath, chnum):
    """
    Returns the stream number for the provided audio. E.g. if the source file has 4 streams in this order:
    Video, Data, 5.1, Stereo - Chs 1-6 would return "2", and 7-8 would return "3".
    """
    if type(chnum) != int:
        raise TypeError(f"chnum parameter must be int not {type(chnum)}")
    elif chnum <= 0:
        raise ValueError(f"chnum must be greater than 0. Got: {chnum}")

    totalchs = audio(filepath, False)
    audiostreams = audio(filepath, True)

    if not totalchs or not audiostreams:
        return False

    if chnum > totalchs:
        raise ValueError(f"chnum is greater than the total number of channels. chnum: {chnum} , total: {totalchs}")

    chcount = 0
    streamindex = False
    for stream in audiostreams:
        chcount += int(stream[1])
        if chcount >= chnum:
            streamindex = stream[0]
            break
    return str(streamindex)
    
def fps(filepath):
    output = all(filepath)

    if not output:
    	return False

    for track in output['tracks']:
        if track['@type'] == "Video":
            return str(track['FrameRate'])

    return False

def tc(filepath):
    """
    Looks for the starting TC in the "Other" track type, under the TimeCode_FirstFrame field.
    If it can't find it, it returns False.
    """
    output = all(filepath)
    if not output:
    	return False

    try:
        tracks = output["tracks"]
    except KeyError:
        return False
    
    othertrk = None
    for trk in tracks:
        if trk["@type"] == "Other":
            othertrk = trk

    if othertrk == None:
        return False

    try:
        tc = othertrk["TimeCode_FirstFrame"]
    except KeyError:
        return False
    else:
        return str(tc)


def streamtypes(filepath):
    """
    Returns a list that contains types for each stream, in order.
    """
    output = all(filepath)
    if not output:
    	return False

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

if __name__ == "__main__":
    testfile = pathlib.Path(r"C:\Mount\rei08\encoding\_FFMPEG_CC_PROXY\_Old\Other\2997_ASM_NDF\Input\gbi_00_final_txtd_178_HQ_20_2997_NDF_wf.mov")
    print(findaudiostream(testfile, 0))