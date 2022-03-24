"""
A straightforward wrapper for the Mediainfo CLI tool. It calls MediaInfo as a subprocess and parses the returning
JSON into formatted datatypes relevent to the information requested.
"""

import sys
import json
import subprocess as sub
from enum import Enum
from pathlib import Path
from typing import Any, Union, Tuple, List, Dict, overload, Literal

if sys.platform == "win32":
    useshell = False
elif sys.platform == "darwin":
    useshell = True
else:
    raise RuntimeError(f"Platform not supported: {sys.platform}")

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
    def __init__(self, filepath: Union[str, Path], mibin: Union[str, Path]) -> None:
        self.filepath = filepath
        self.mibin = mibin
        self.fulljson: Dict[Any,Any] = self.get_json(raw=False)

    @overload
    def get_json(self, raw: Literal[False]) -> Dict[Any,Any]:...
    @overload
    def get_json(self, raw: Literal[True]) -> bytes:...
    def get_json(self, raw: bool=False):
        """
        This method communicates with the MediaInfo binary directly and returns the results.

        It returns a dictionary with 2 keys: 'path' and 'tracks'. 'path' is the original path
        that was passed into this static method. 'tracks' contains a list of tracks where each
        track is a dictionary that contains properties for that track.

        If raw=True it will return the unchanged JSON output(as bytes) straight from the Mediainfo CLI.
        """
        if not Path(self.filepath).is_file():
            raise FileNotFoundError(f"\'{self.filepath}\' is not a path to a file or does not exist")

        filepath = f'"{str(self.filepath)}"' if " " in str(self.filepath) else self.filepath

        miproc = sub.Popen(f"{str(self.mibin)} {str(filepath)} --output=JSON", stdin=sub.PIPE, stdout=sub.PIPE, stderr=sub.PIPE, shell=useshell)
        rawbytes = miproc.stdout.read() #type:ignore
        if raw:
            return rawbytes

        rawstr = rawbytes.decode('utf-8')
        try:
            fileoutput = json.loads(rawstr)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Unable to decode JSON from MediaInfo. JSON decode error: {e}") #type:ignore

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

    @overload
    def video(self, streams: Literal[False]=False, pids: bool=False) -> int:...
    @overload
    def video(self, streams: Literal[True]=True, pids: bool=False) -> List[int]:...
    def video(self, streams: bool=False, pids: bool=False):
        """
        Returns the total number of video channels as an int.

        If 'streams=True', it instead returns a list containing the index of each video stream.
        If 'pids=True', it returns the pids instead of the stream index.
        """
        videostreams = []

        if pids:
            datafield = 'ID'
        else:
            datafield = 'StreamOrder'

        for track in self.fulljson['tracks']:
            if track["@type"] == 'Video':
                videostreams.append(int(track[datafield]))

        if not videostreams:
            return [] if streams else 0

        if streams:
            return videostreams
        else:
            return len(videostreams)

    @overload
    def audio(self, streams: Literal[False]=False, pids: bool=False) -> int:...
    @overload
    def audio(self, streams: Literal[True]=True, pids: bool=False) -> List[Tuple[int,int]]:...
    def audio(self, streams: bool=False, pids: bool=False):
        """
        Returns the total number of audio channels as an int.

        If 'streams=True', it instead returns a list of tuples.
        The tuples contain the index of the stream and the number of channels in that stream.
        If 'pids=True', it returns the pids in the first pos of the tuple instead of the stream index.
        """
        chs_perstream = []
        audiostreams = []

        if pids:
            datafield = 'ID'
        else:
            datafield = 'StreamOrder'

        for track in self.fulljson['tracks']:
            if track["@type"] == 'Audio':
                chs_perstream.append(int(track['Channels']))
                audiostreams.append(int(track[datafield]))

        if not audiostreams:
            return [] if streams else 0

        if streams:
            return list(zip(audiostreams, chs_perstream))
        else:
            return sum(chs_perstream)


    def fps(self) -> Union[str, None]:
        for track in self.fulljson['tracks']:
            if track['@type'] == "Video":
                return track.get('FrameRate', None)


    def streamtypes(self) -> List[str]:
        """
        Returns a list that contains types for each stream, in order.
        """
        alltypes = []
        order = []

        for track in self.fulljson['tracks']:
            if track['@type'] != 'General':
                if track['@type'] == 'Image':
                    return ['Image']
                alltypes.append(track['@type'])
                streamorder = track.get('StreamOrder', None)
                if not streamorder:
                    streamorder = track.get("@typeorder", None)
                    if not streamorder:
                        raise TypeError("MediaInfo is unable to get the stream order.")
                order.append(streamorder)
        
        if not alltypes:
            return []

        tosort = [x for x in zip(alltypes, order)]
        tosort.sort(key= lambda x:x[1])
        sorted = [x[0] for x in tosort]

        return sorted


    def framecount(self) -> Union[str, None]:
        """
        Returns the total number of frames.
        """
        for track in self.fulljson['tracks']:
            if track['@type'] == "General":
                return track.get('FrameCount', None)


    def duration(self) -> Union[str, None]:
        """
        Returns the total duration in seconds.
        """
        for track in self.fulljson['tracks']:
            if track['@type'] == "General":
                return track.get('Duration', None)


    def start_tc(self) -> Union[str, None]:
        """
        Returns the starting TC listed in the "Other" track, if available.
        """
        for track in self.fulljson['tracks']:
            if track['@type'] == "Other":
                return track.get('TimeCode_FirstFrame', None)


    def colorspace(self) -> Union[str, None]:
        for track in self.fulljson['tracks']:
            if track['@type'] == 'Video':
                return track.get('ColorSpace', None)
        for track in self.fulljson['tracks']:
            if track['@type'] == 'Image':
                return track.get('ColorSpace', None)


    @overload
    def resolution(self, asint: Literal[True]) -> Tuple[int, int] | None:...
    @overload
    def resolution(self, asint: Literal[False]) -> Tuple[str, str] | None:...
    def resolution(self, asint: bool=False):
        width, height = None, None
        for track in self.fulljson['tracks']:
            if track['@type'] == 'Video':
                width = track.get('Width', None)
                height = track.get('Height', None)
        for track in self.fulljson['tracks']:
            if track['@type'] == 'Image':
                width = track.get('Width', None)
                height = track.get('Height', None)

        if width == None or height == None:
            return None
        if asint:
            return (int(width), int(height))
        else:
            return (str(width), str(height))


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
