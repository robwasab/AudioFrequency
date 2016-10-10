from FastFilter import FastFilter
import numpy as np

class Channel(FastFilter):

	def __init__(self, *args, **kwargs):
		kwargs['flush'] = True
		FastFilter.__init__(self, *args, **kwargs)
		for kw in kwargs:
			if kw == 'distor' or kw == 'distortion':
				self.distor = kwargs[kw]
	
	def process(self, msg):
		pad = 1024 - len(msg)%1024
		return np.append(msg, np.zeros(pad))
