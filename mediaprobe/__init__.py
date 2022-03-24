"""
A straightforward wrapper for the Mediainfo CLI tool. It calls mediainfo as a subprocess and parses the returning
JSON into formatted datatypes relevent to the function called.
"""

from .attributes import MediaAttributes, MediaProbe