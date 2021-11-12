from enum import Enum

class tracktypes(Enum):
    video = "video"
    audio = "audio"
    image = "image"
    data = "data"
    other = "other"

tracktypes('test')