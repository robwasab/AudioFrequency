from   Parent.Module  import Module
from   Functions.util import quantize
import numpy as np
import pdb

class TimingRecovery(Module):
	def __init__(self, *args, **kwargs):
		Module.__init__(self, *args, **kwargs)
		self.alphabet = [-3, -1, 1, 3]
		try:
			self.M = int(kwargs['M'])
			self.log('M: %d'%self.M)
		except KeyError as ke:
			print self.FAIL+'You must pass ' + str(ke) + ' as key word argument'
			raise ke

		#self.offset = int(np.random.rand()*2*self.M)
		self.save1 = 0
		self.save2 = 0
		self.save3 = 0
		self.offset = 1

	def process(self, data):
		down_samples = np.zeros(2*len(data)/self.M)
		step = self.M 

		k = 0
		if self.offset == 0:
			self.log('using saved data, offset 0')
			self.save3 = data[1]
			self.save2 = data[0]
			dy_doffset = (quantize(self.save2, self.alphabet) - self.save2)*(self.save3 - self.save1)
			self.offset += step * dy_doffset
			down_samples[0] = data[0]
			k = 1
		elif self.offset == -1:
			self.log('using saved data, offset -1')
			self.save3 = data[0]
			dy_doffset = (quantize(self.save2, self.alphabet) - self.save2)*(self.save3 - self.save1)
			self.offset += step * dy_doffset
			down_samples[0] = self.save2
			k = 1

		while True:
			n = int(round(self.M*k + self.offset))
			if n + 1 == len(data):
				self.save2 = data[n]
				self.save1 = data[n-1]
				self.offset= -1
				break
			elif n == len(data):
				self.save1 = data[n-1]
				self.offset= 0
				break
			elif n > len(data):
				self.offset= n - len(data)
				break
			down_samples[k] = data[n]
			k += 1
			dy_doffset = (quantize(data[n], self.alphabet) - data[n])*(data[n+1] - data[n-1])
			self.offset += step * dy_doffset

		return down_samples[:k]

		#for skip_by_m in range(self.start_index, len(data), self.M):
		#	#print self.offset
		#	n = int(round(skip_by_m + self.offset))
		#	if n >= len(data)-1:
		#		self.start_index = n - len(data)+1
		#		self.offset = 0
		#		break
		#	down_samples[down_samples_index] = data[n]
		#	down_samples_index += 1
		#	if down_samples_index >= len(down_samples):
		#		#shouldn't get here
		#		raise Exception('TimingRecovery: Shouldn\'t get here...')
		#		break

		#	dy_doffset = (quantize(data[n], self.alphabet) - data[n]) * (data[n+1] - data[n-1])
		#	self.offset += step * dy_doffset
		#
		#print self.BLUE + 'down_samples_index [%d/%d]'%(down_samples_index, len(data)/self.M)
		#if self.debug:
		#	self.log('adaptation offset: %.3f'%self.offset)
		#return down_samples[1:down_samples_index]

class Queue(object):
	def __init__(self, memory_type = np.float16, memory_size = 1024):
		self.memory_size = memory_size
		self.memory = np.zeros(self.memory_size, memory_type)
		self.quhead = 0
		self.qutail = 0
		self.qusize = 0

	def resize(self, size):
		self.memory_size = size
		self.memory = np.zeros(self.memory_size)
		self.quhead = 0
		self.qutail = 0
		self.qusize = 0

	def size(self):
		size = self.qusize
		return size

	def put(self, data):
		room = len(data) > self.memory_size - self.qusize;

		if room:
			raise Full("Not enough room in queue")
		
		indexes = (self.qutail + np.arange(len(data)))%self.memory_size
		self.memory[indexes] = data
		self.qusize += len(data)
		self.qutail += len(data)

	def read(self, amt):
		if amt > self.size():
			raise Empty("Not enough data to read from")
		
		indexes = (self.quhead + np.arange(amt))%self.memory_size
		self.qusize -= amt
		retreive = self.memory[indexes]
		self.quhead  = (self.quhead + amt)%self.memory_size
		read = self.memory[indexes]
		return read

	def print_memory(self):
		colsize = int(np.sqrt(len(self.memory)))
		rowsize = len(self.memory_size)/colsize;

		print "col x row = %d"%(colsize*rowsize)

		for y in range(rowsize-1, -1, -1):
			line = '%4d: ['%(y*colsize)
			for x in range(0, colsize):
				line += '\t%5.3f\t'%self.memory[y*colsize + x]
			line += ']\n'
			print line

