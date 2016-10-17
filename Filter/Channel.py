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
		return FastFilter.process(self, msg)
