from Parent.Module import Module
from Queue import Queue
from time import time,sleep
import numpy as np

class Microphone(Module):
	def __init__(self, *args, **kwargs):
		Module.__init__(self, *args, **kwargs)
		self.chunk_size = 1024
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
		if self.save is not None:
			data = np.append(self.save, data)

		if len(data) > self.chunk_size:
			N = int(len(data)/self.chunk_size)
			for n in xrange(0,N):
				self.output.input.put(data[n*self.chunk_size:(n+1)*self.chunk_size])

			self.save = data[-(len(data)%self.chunk_size):]
		else:
			self.save = data
		return None
