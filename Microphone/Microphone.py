from Parent.Module import Module
from time import time,sleep
from Queue import Queue
import numpy as np
import pyaudio
import wave
import sys
import pdb

class Microphone(Module):
	def __init__(self, *args, **kwargs):
		Module.__init__(self, *args, **kwargs)
		self.chunk_size = 2**9
		for kw in kwargs:
			if kw == 'chunk_size':
				self.chunk_size = kwargs[kw]

		self.save = None

	def process(self, data):
		pad = np.zeros((self.chunk_size - (len(data)%self.chunk_size)))
		data = np.append(data, pad)
		self.log('len(data): %d'%len(data))

		N = int(len(data)/self.chunk_size)
		self.log('Breaking into %d chunks'%N)
		#noise = 0.1 * (np.random.rand(len(data))-0.5)
		#data = noise + data
		#data *= 0.1
		for n in xrange(0,N):
			self.output.input.put(data[n*self.chunk_size:(n+1)*self.chunk_size])
		if self.scope is not None:
			self.scope.set_fft(True)
			self.scope.set_fft_fs(44.1E3)
			self.scope.put(data)
		return None
