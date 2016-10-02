from   Parent.Module import Module
import numpy as np

class Whitener(Module):
	def __init__(self, *args, **kwargs):
		Module.__init__(self, *args, **kwargs)
		kw = ''
		try:
			kw = 'cipher'
			self.cipher = kwargs[kw]
			self.n = len(self.cipher)
			self.incomplete = 0
		except KeyError as ke:
			self.print_kw_error(kw)
			raise(kw)
		self.log(self.cipher)
	
	def reset(self):
		Module.reset(self)
		self.incomplete = 0
	
	def process(self, data):
		if self.incomplete > 0:
			if self.incomplete > len(data):
				offset = self.n - self.incomplete
				data = np.bitwise_xor(data,self.cipher[offset:offset+len(data)])
				self.incomplete -= len(data)

				if self.debug:
					self.log('incomplete   : %d'%self.incomplete)
					self.log('wavelet size : %d'%self.n)
				return data
			else:
				data[0:self.incomplete] = np.bitwise_xor(data[0:self.incomplete], self.cipher[-self.incomplete:])

		for k in xrange(self.incomplete,len(data),self.n):
			if k+self.n > len(data):
				leftover = len(data)-k
				if self.debug:
					self.log('leftover     : %d'%leftover)

				data[k:k+leftover] = np.bitwise_xor(data[k:k+leftover], self.cipher[:leftover])

				self.incomplete = self.n - leftover 
				if self.debug:
					self.log('incomplete   : %d'%self.incomplete)
					self.log('wavelet size : %d'%self.n)
			else:
				data[k:k+self.n] = np.bitwise_xor(data[k:k+self.n], self.cipher)
		return data
