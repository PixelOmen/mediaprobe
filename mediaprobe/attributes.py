from pathlib import Path
from dataclasses import dataclass
from typing import overload, Literal

from .main import MediaProbe

@dataclass(slots=True)
class MediaAttributes:
	"""
	A struct-like dataclass that contains many of the commonly used MediaInfo fields as attributes.
	It uses an instance of the MediaProbe class to gather most of the information, which can be
	accessed directly via the 'probe' attribute.
	"""
	filepath: Path
	probe: MediaProbe
	streamcount: int
	streamtypes: list[str]
	videolocations: list[int]
	audiolocations: list[tuple[int,...]]
	audiocount: int
	videocount: int
	fps: float | None=None
	resolution: tuple[int,int] | None=None
	framecount: int | None=None
	start_tc: str | None=None


	def __init__(self, srcfile: str|Path, mibin: str|Path, raise_if_none: bool=True):
		""" If raise_if_none=True (default), it will raise an exception if unable to parse framerate, resolution, or framecount"""
		self.filepath = Path(srcfile)
		self.probe = MediaProbe(self.filepath, mibin)
		self.fps = None if self.probe.fps() == None else float(str(self.probe.fps()))
		self.resolution = self.probe.resolution(asint=True)
		self.framecount = None if self.probe.framecount() == None else int(str(self.probe.framecount()))
		self.streamtypes = self.probe.streamtypes()
		self.streamcount = len(self.streamtypes)
		self.videocount = self.probe.video()
		self.videolocations = self.probe.video(streams=True)
		self.audiocount = self.probe.audio()
		self.audiolocations = self.probe.audio(streams=True)
		self.start_tc = self.probe.start_tc()
		if raise_if_none:
			self.raise_if_none()

	def raise_if_none(self) -> None:
		""" Raises an exception if unable to parse framerate, resolution, or framecount"""
		nonetypes = {
			"framerate": self.fps,
			"resolution": self.resolution,
			"framecount": self.framecount,
		}
		for name, attr in nonetypes.items():
			if attr is None:
				raise AttributeError(f"Unable to get {name} for {self.filepath}")

	@overload
	def find_audiostream(self, ch: int, ffcmd: Literal[False]=False) -> int|None:...
	@overload
	def find_audiostream(self, ch: int, ffcmd: Literal[True]=True) -> str|None:...
	def find_audiostream(self, ch: int, ffcmd: bool=False) -> int|str|None:
		"""
		If ffcmd=False (default), this return the stream number where an audio channel is located.
		If ffcmd=True, this constructs the FFMPEG mapping command needed to extract that specific audio channel.
		"""
		if self.audiocount == None:
			raise ValueError(f'Cannot find stream because MediaAttributes.audiocount = None.')
		if ch > self.audiocount or ch <= 0:
			return None

		streamindexes, streamchs = list(zip(*self.audiolocations))

		prev_streamtotal = 0
		streamindex = None
		for index, stream_chs in enumerate(streamchs):
			stream_chs = int(stream_chs)
			current_total = prev_streamtotal + stream_chs
			if current_total >= ch:
				streamindex = index
				break		
			prev_streamtotal = current_total

		if streamindex == None:
			return None

		foundstream = streamindexes[streamindex]

		if not ffcmd:
			return foundstream

		ch_diff = (ch - prev_streamtotal) - 1
		if int(streamchs[streamindex]) == 1:
			return f"-map 0:{foundstream}"
		elif int(streamchs[streamindex]) == 2:
			if ch_diff == 0:
				layout = "FL"
				layoutvar = "left"
			else:
				layout = "FR"
				layoutvar = "right"
			return f'-filter_complex "[0:{foundstream}]channelsplit=channel_layout=stereo:channels={layout}[{layoutvar}]" -map "[{layoutvar}]"'
		elif int(streamchs[streamindex]) > 2:
			return f"-map_channel 0.{foundstream}.{ch_diff}"
		else:
			raise ValueError("Something went wrong locating audiostream. " +
							f"Channel={ch} Totalstreams={self.audiocount} Audiostreams={self.audiolocations}")