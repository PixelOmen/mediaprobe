"""
A straightforward wrapper for the Mediainfo CLI tool. It calls MediaInfo as a subprocess and parses the returning
JSON into formatted datatypes relevent to the function called.
"""

import sys
import json
import subprocess as sub
from pathlib import Path
from typing import Union
from enum import Enum

# testfile constant and binary path initialization
TESTFILE = r"\\10.0.20.175\rei08\DCI\testing\_Testfiles\Logan_8Ch.mov"

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

class Tracktypes(Enum):
    general = "General"
    video = "Video"
    audio = "Audio"
    image = "Image"
    data = "Data"
    other = "Other"

def get_tracktype_enum(trk_type: str) -> Tracktypes:
    return Tracktypes(trk_type.lower().capitalize())

class MediaProbe:
    def __init__(self, filepath: Union[str, Path]) -> None:
        self.filepath = filepath
        self.fulljson = MediaProbe.get_json(filepath)

    @staticmethod
    def get_json(filepath: Union[str, Path], raw: bool=False) -> Union[dict, bytes]:
        """
        This is a 'pure' static method. It does alter any state or variables anywhere.
        It communicates with the MediaInfo binary directly and returns the results.

        It returns a dictionary with 2 keys: 'path' and 'tracks'. 'path' is the original path
        that was passed into this static method. 'tracks' contains a list of tracks where each
        track is a dictionary that contains properties for that track.

        If raw=True it will return the unchanged JSON output(as bytes) straight from the Mediainfo CLI.
        """
        if not Path(filepath).is_file():
            raise FileNotFoundError(f"'{filepath}' is not a path to a file or does not exist")

        if " " in str(filepath):
            filepath = f'"{str(filepath)}"'

        miproc = sub.Popen(f"{str(mibin)} {str(filepath)} --output=JSON", stdin=sub.PIPE, stdout=sub.PIPE, stderr=sub.PIPE, shell=useshell)
        rawbytes = miproc.stdout.read()
        if raw:
            return rawbytes

        rawstr = rawbytes.decode('utf-8')
        try:
            fileoutput = json.loads(rawstr)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Unable to decode JSON from MediaInfo. JSON decode error: {e}")

        if fileoutput == None:
            raise BufferError("Didn't read anything from MediaInfo")

        fileoutput = fileoutput['media']

        path = fileoutput['@ref']
        del fileoutput['@ref']
        fileoutput['path'] = path

        tracks = fileoutput['track']
        del fileoutput['track']
        fileoutput['tracks'] = tracks

        return dict(fileoutput)

    def printall(self) -> None:
        ''' "Pretty" print the full contents of MediaInfo's JSON output'''
        print('\n')
        print(self.fulljson['path'])
        for track in self.fulljson['tracks']:
            for k,v in track.items():
                if k == "@type":
                    print("\n")
                print(f"{k} = {v}")

    def audio(self, tracks: bool=False, pids: bool=False) -> Union[int, list, None]:
        """
        Returns the total number of audio channels as an int.

        If 'tracks=True', it instead returns a list of tuples.
        The tuples contain the index of the stream and the number of channels in that stream.
        If 'pids=True', it returns the pids in the first pos of the tuple instead of the stream order.
        """
        chspertrack = []
        trackorder = []

        if pids:
            datafield = 'ID'
        else:
            datafield = 'StreamOrder'

        for track in self.fulljson['tracks']:
            if track["@type"] == 'Audio':
                chspertrack.append(track['Channels'])
                trackorder.append(track[datafield])

        if not chspertrack and not trackorder:
            return None

        if tracks:
            return list(zip(trackorder, chspertrack))
        else:
            totalchs = 0
            for ch in chspertrack:
                totalchs += int(ch)
            return int(totalchs)

    def fps(self) -> Union[str, None]:
        for track in self.fulljson['tracks']:
            if track['@type'] == "Video":
                return track.get('FrameRate', None)

    def streamtypes(self) -> Union[list, None]:
        """
        Returns a list that contains types for each stream, in order.
        """
        alltypes = []
        order = []

        for track in self.fulljson['tracks']:
            if track['@type'] != 'General':
                alltypes.append(track['@type'])
                order.append(track['StreamOrder'])

        tosort = [x for x in zip(alltypes, order)]
        tosort.sort(key= lambda x:x[1])
        sorted = [x[0] for x in tosort]

        return sorted

    def framecount(self) -> Union[str, None]:
        """
        Returns the total number of frames.
        """
        for track in self.fulljson['tracks']:
            if track['@type'] == "Video":
                return track.get('FrameCount', None)

    def duration(self) -> Union[str, None]:
        """
        Returns the total duration in seconds.
        """
        for track in self.fulljson['tracks']:
            if track['@type'] == "Video":
                return track.get('Duration', None)

    def start_tc(self) -> Union[str, None]:
        """
        Returns the starting TC listed in the "Other" track, if available.
        """
        for track in self.fulljson['tracks']:
            if track['@type'] == "Other":
                return track.get('TimeCode_FirstFrame', None)

    def colorspace(self) -> Union[str, None]:
        if not self.fulljson:
            return None
        for track in self.fulljson['tracks']:
            if track['@type'] == 'Video':
                return track.get('ColorSpace', None)
        for track in self.fulljson['tracks']:
            if track['@type'] == 'Image':
                return track.get('ColorSpace', None)

    def search(self, searchterm: str, tracktype: Union[str, Tracktypes]) -> Union[str, None]:
        if isinstance(tracktype, str):
            try:
                tracktype = get_tracktype_enum(tracktype)
            except ValueError:
                print((f"Invalid tracktype: {tracktype}"))
                return None

        for track in self.fulljson['tracks']:
            if track['@type'] == tracktype.value:
                return track.get(searchterm, None)


if __name__ == "__main__":
    probe = MediaProbe(TESTFILE)
    print(probe.search("Format_Profile", "vIdEo"))
