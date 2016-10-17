from Parent.Module import Module
import matplotlib.pyplot as plt
from time import time,sleep
from Queue import Queue
import numpy as np
import pyaudio
import wave
import pdb

class Microphone(Module):
	def __init__(self, *args, **kwargs):
		Module.__init__(self, *args, **kwargs)
		self.chunk_size = 2**9
		for kw in kwargs:
			if kw == 'chunk_size':
				self.chunk_size = kwargs[kw]

		self.save = None

	def work(self):
		if not self.input.empty():
			in_data = self.input.get()
			if self.passthrough == True:
				self.output.input.put(in_data)
				return True
			start = time()
			self.process(in_data)
			stop  = time()
			print self.YELLOW + self.__class__.__name__+':\t [%4.3f ms]'%(1000.0*(stop-start))+self.ENDC
			return True
		else:
			return False

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
		return None
