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
		self.chunk_size = 2**10 
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

	def save_data(self, data):
		np.savetxt('microphone_data.gz', data)

	def process(self, data):
		#self.save_data(data)
		pad = np.zeros((self.chunk_size - len(data)%self.chunk_size))
		data = np.append(data, pad)
		self.log('len(data): %d'%len(data))

		N = int(len(data)/self.chunk_size)
		self.log('Breaking into %d chunks'%N)
		noise = 0.1 * (np.random.rand(len(data))-0.5)
		data = noise + data
		data *= 0.1
		for n in xrange(0,N):
			self.output.input.put(data[n*self.chunk_size:(n+1)*self.chunk_size])
		return None

	def visualize(self):
		CHUNK = 2**12
		FORMAT = pyaudio.paInt16
		CHANNELS = 1
		RATE = 44100
		p = pyaudio.PyAudio()
		stream = p.open(format=FORMAT, 
				channels=CHANNELS,
				rate=RATE,
				input=True,
				frames_per_buffer=CHUNK)
		
		buffer = np.zeros(CHUNK*4)
		tail = 0
		plt.figure(1)
		handle, = plt.plot(buffer)
		plt.gcf().gca().set_ylim((2**15-1,-2**15))
		plt.show(block=False)
		try:
			while True:
				data = np.fromstring(stream.read(CHUNK),dtype=np.int16)
				indecies = np.arange(tail, tail+len(data)) % len(buffer)
				tail = indecies[-1]
				buffer[indecies] = data
				#handle.set_ydata(buffer)	
				#plt.gcf().canvas.draw()

		except KeyboardInterrupt:
			stream.stop_stream()
			stream.close()
			p.terminate()

