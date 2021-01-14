# Mediaprobe

A straightforward wrapper for the Mediainfo CLI tool. It calls mediainfo as a subprocess and parses the returning JSON into formatted datatypes relevent to the function called.

---

## Installation

#### DIRECT PYTHON INSTALL

To install checked out source code:

```bash
python[#] setup.py install
```

To install the library in develop mode (similar to `pip install -e`), run:

```bash
python[#] setup.py develop
```

#### Pip Install

Coming Soon

## Usage

```python
import mediaprobe

mediaprobe.fps('/path/to/file.mov')
# returns the file's framerate as a string
mediaprobe.audio('/path/to/file.mov')
# returns total number of audio as int
mediaprobe.audio('/path/to/file.mov', tracks=True) 
# returns list of tuples with total channels per stream and stream order
mediaprobe.streamtypes('/path/to/file.mov')
# returns a list of types e.g. ["Video", "Audio", "Audio", "Data"] in order

allinfo = mediaprobe.all('/path/to/file.mov')
# returns dict with full output of mediainfo
allinfo['tracks'][1]['OverallBitRate']
# pull any other desired info out of track
```
##### More utility functions will eventually be added.

## Contributing
Pull requests are welcome. 

## License
[MIT](https://choosealicense.com/licenses/mit/)