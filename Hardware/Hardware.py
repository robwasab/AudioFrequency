from Parent.Module import Module
#import matplotlib.pyplot as plt
from time import time,sleep
from Queue import Queue
import numpy as np
import pyaudio
import wave
import pdb
from   numpy.fft import fft
import sys

#size = 2**10
#buffer = np.zeros(size)
#freqs = np.arange(size)/float(size)*44.1E3
#ax = plt.subplot(111)
#handle, = ax.plot(freqs, buffer)
#ax.set_xlim((freqs[0], freqs[-1]))
#ax.set_ylim((0, 1.0))
#plt.show(block = False)

class Microphone(Module):
	def __init__(self, *args, **kwargs):
		Module.__init__(self, *args, **kwargs)
		self.chunk_size = 2**10
		self.fs = 44.1E3
		for kw in kwargs:
			if kw == 'chunk_size':
				self.chunk_size = kwargs[kw]
			if kw == 'fs':
				self.fs = kwargs[kw]


	def start(self):
		self.p = pyaudio.PyAudio()
		self.stream = self.p.open(
				format=pyaudio.paFloat32,
				channels=1,
				rate=int(self.fs),
				input=True,
				frames_per_buffer=self.chunk_size,
				stream_callback=self.callback)
		self.stream.start_stream()
		Module.start(self)
	
	def callback(self, in_data, frame_count, time_info, status):
		audio = np.fromstring(in_data, dtype=np.float32)
		power = np.sum(audio**2)
		if self.output is not None and power > 0.25:
			self.output.input.put(audio)
			if self.scope is not None:
				self.scope.set_fft(True)
				self.scope.set_fft_fs(44.1E3)
				self.scope.put(audio)
		return (audio, pyaudio.paContinue)
	
	def quit(self, all):
		self.stream.stop_stream()
		self.stream.close()
		self.p.terminate()	
		Module.quit(self, all)

class Speaker(Module):
	def __init__(self, *args, **kwargs):
		Module.__init__(self, *args, **kwargs)
		self.chunk_size = 2**10
		self.fs = 44.1E3

		for kw in kwargs:
			if kw == 'chunk_size':
				self.chunk_size = kwargs[kw]
			if kw == 'fs':
				self.fs = kwargs[kw]
		self.p = None
		self.stream = None

	def start(self):
		self.p = pyaudio.PyAudio()
		self.stream = self.p.open(
				format=pyaudio.paFloat32,
				channels=1,
				rate=int(self.fs),
				output=True)
		Module.start(self)

	def process(self, data):
		if self.stream is not None:
			self.stream.write(data.astype(np.float32).tostring())
		return None
	
	def quit(self, all):
		self.stream.stop_stream()
		self.stream.close()
		self.p.terminate()	
		Module.quit(self, all)
