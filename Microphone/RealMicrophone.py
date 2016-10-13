from Parent.Module import Module
import matplotlib.pyplot as plt
from time import time,sleep
from Queue import Queue
import numpy as np
import pyaudio
import wave
import pdb

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

class Microphone(Module):
	def __init__(self, *args, **kwargs):
		Module.__init__(self, *args, **kwargs)
		self.chunk_size = 2**10 
		for kw in kwargs:
			if kw == 'chunk_size':
				self.chunk_size = kwargs[kw]

		p = pyaudio.PyAudio()
		stream = p.open(format=FORMAT, 
				channels=CHANNELS,
				rate=RATE,
				input=True,
				frames_per_buffer=CHUNK)

		self.stream = stream
		self.p = p

	def work(self):
		#self.output.input.put(
		#np.fromstring(self.stream.read(CHUNK),dtype=np.int16))
		np.fromstring(self.stream.read(CHUNK),dtype=np.float64)
	
	def quit(self):
		self.stream.stop_stream()
		self.stream.close()
		self.p.terminate()
		Module.quit(self)
