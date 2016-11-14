from FastFilter import FastFilter
import numpy as np
import pdb

class Channel(FastFilter):

	def __init__(self, *args, **kwargs):
		kwargs['flush'] = True
		for kw in kwargs:
			if kw == 'distor' or kw == 'distortion':
				self.distor = kwargs[kw]
				kwargs['bcoef'] = kwargs[kw]
		self.log(kwargs['bcoef'])
		FastFilter.__init__(self, *args, **kwargs)
	
	def process(self, msg):
		if self.scope is not None:
			self.scope.set_fft(True)
			self.scope.set_fft_fs(44.1E3)
			self.scope.set_size(len(self.bcoef))
			self.scope.put(self.bcoef)
		return FastFilter.process(self, msg)
