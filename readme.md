# Mediaprobe

A straightforward wrapper for the Mediainfo CLI tool. It calls MediaInfo as a subprocess and parses the returning
JSON into formatted datatypes relevent to the information requested.

The package provides two main classes: MediaProbe and MediaAttributes.
___

### MediaProbe and MediaAttributes
MediaProbe provides information via the instantiated object's method calls, e.g. `testobject.fps()`. This class can be used directly, but it is also used in the constructor for `MediaAttributes` and stored in the `probe` attribute of that class.

MediaAttributes uses the newer type hinting syntax (≥3.10), provides a `dataclass` with `slots`, and uses a more struct-like syntax for accessing the media's information via attributes, e.g. `testobject.fps`.

MediaAttributes also has a special method that can either return the stream number where an audio channel is located, or construct the FFMPEG mapping command needed to extract that specific audio channel. See usage below for more information.

___

## Installation

### Direct Python Install:

```bash
python setup.py install
```

---

## MediaProbe Usage

```python
from mediaprobe import MediaProbe

testfile = '/path/to/file.mov'
mediainfobin = '/path/to/mediainfo.exe'

testprobe = MediaProbe(testfile, mediainfobin)

# returns the file's framerate as a string
testprobe.fps()
# 23.976

# returns total number of audio channels as int
testprobe.audio()
# 6

# returns list of tuples with the stream order and channels per stream. Mono streams example:
testprobe.audio(streams=True)
# [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1)]

# returns a list of track types in order
testprobe.streamtypes()
# ["Video", "Audio", "Audio", "Data"]

# "Pretty" prints the full output from MediaInfo
testprobe.printall()

# Access the full json output as a dict
testprobe.fulljson['tracks'][0]['OverallBitRate']
# 181929314

# Search for specific fields in the mediainfo output. This example would return '422 HQ' from a ProRes422HQ
testprobe.search("Format_Profile", "video")
# 422 HQ
```

---
## MediaAttributes Usage

```python
from mediaprobe import MediaAttributes

testfile = '/path/to/file.mov'
mediainfobin = '/path/to/mediainfo.exe'

testprobe = MediaAttributes(testfile, mediainfobin)

# returns the file's framerate as a float
testprobe.fps
# 23.976

# returns total number of audio channels as int
testprobe.audiocount
# 6

# returns list of tuples with the stream order and channels per stream. Mono streams example:
testprobe.audiolocations
# [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1)]

# returns a list of track types in order
testprobe.streamtypes
# ["Video", "Audio", "Audio", "Data"]

# MediaAttribute objects still contain access to the underlying MediaProbe object:
testprobe.probe.printall()
testprobe.probe.fulljson['tracks'][0]['OverallBitRate']
# 181929314
testprobe.probe.search("Format_Profile", "video")
# 422 HQ

# Get the stream where audio channel is located (mono stream example)
testprobe.find_audiostream(5)
# 5

# Get the stream where audio channel is located (5.1 + Stereo example)
testprobe.find_audiostream(5)
# 1 (stream 0 being the video stream)

# Get the FFMPEG mapping command to extract the audio (5.1 + Stereo example)
testprobe.find_audiostream(5, ffcmd=True)
# -map_channel 0.2.4
testprobe.find_audiostream(7, ffcmd=True)
# -filter_complex "[0:3]channelsplit=channel_layout=stereo:channels=FL[left]" -map "[left]"
```

---
##
## Contributing
Pull requests are welcome. 

## License
[MIT](https://choosealicense.com/licenses/mit/)