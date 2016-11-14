from   Filter.FastFilter import FastFilter
from   Functions.util    import quantize
from   Whitener.Whitener import Whitener
from   Queue import Full, Empty
from   struct import unpack
import numpy as np
import pdb

class FrameSync(FastFilter):
	def __init__(self, *args, **kwargs):
		kw = ''
		try:
			kw = 'prefix'
			corr_prefix  = np.fliplr([kwargs[kw]])[0].astype(float)
			corr_prefix_power = np.sum(corr_prefix**2)
			corr_prefix /= corr_prefix_power
			self.corr_prefix_power = corr_prefix_power

			kwargs['bcoef'] = corr_prefix
			FastFilter.__init__(self, *args, **kwargs)

			kw = 'cipher'
			self.cipher = kwargs[kw]

			self.queue = Queue(np.float64, 2**12)
			self.state = 'look_for_header'
			self.thresh = 0.5
			if self.box is not None:
				self.msg_prog = self.box.add_label('msg prog: [0/0]')
			
		except KeyError as ke:
			self.print_kw_error(kw)
			raise(ke)

		self.whiten = Whitener(cipher = self.cipher, diable=False)
		self.inv = 1

	def pam2num(self, pam):
		return [n for n in [np.sum(quad << np.arange(len(quad)-1,-1,-1)*2) for quad in np.reshape((np.array(pam)+3)/2,(len(pam)/4,4))]]

	def num2text(self, num):
		return ''.join([chr(b) for b in num])


	def process(self, data):
		index, s = self.conv_chunk_chunk(data, fsync_hack=True, flush=False)

		if index != -1:
			self.state = 'read_payload_len'
			self.inv = s
			self.queue.read(self.queue.size())
			self.queue.put(self.inv*data[index+1:])
			self.reset()
			self.whiten.reset()
			self.log('FOUND START OF PAYLOAD!')
			self.blog('Found header!')

		elif index == -1:
			if self.state == 'look_for_header':
				return None
			# All other states add data to queue
			else:
				#self.log('storing data...');
				if self.queue.memory_size - self.queue.size() < len(data):
					self.queue.read(self.queue.size())
				self.queue.put(data*self.inv)

		if self.state == 'read_payload_len':
			if self.queue.size() > 8:
				pam = [quantize(d) for d in self.queue.read(8)]
				num_bytes = self.whiten.process(self.pam2num(pam))
				#num_bytes = self.pam2num(pam)
				self.num_bytes = (num_bytes[1] << 8) + num_bytes[0] + 1
				self.log('num_bytes: %d'%self.num_bytes)
				self.log('bytes in queue: %f'%(self.queue.size()/4.0))
				self.print_pam(pam)
				self.state = 'read_payload'
		text = None

		if self.state == 'read_payload':

			if self.queue.size() >= 4 * self.num_bytes:
				pam = [quantize(d) for d in self.queue.read(4*self.num_bytes)]
				payload = self.pam2num(pam)
				#self.log('payload before whitening: ' + str(payload))
				payload = self.whiten.process(payload)
				#self.log('payload after  whitening: ' + str(payload))
				text = self.num2text(payload)	
				self.state = 'look_for_header'
				self.queue.read(self.queue.size())
				self.num_bytes = 0

			if self.box is not None:
				msg_prog_txt = 'msg prog: [%.3f/%d]'%(self.queue.size()/4.0, self.num_bytes)
				self.box.notify(self.msg_prog, msg_prog_txt)
		return text 

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

	def reset(self):
		self.quhead = 0
		self.qutail = 0
		self.qusize = 0

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

