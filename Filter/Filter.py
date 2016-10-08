from   Parent.Module import Module
import numpy as np

class FirFilter(Module):
	def __init__(self, *args, **kwargs):
		kw = ''
		try:
			kw = 'bcoef'
			self.bcoef = np.array(kwargs[kw])
		except KeyError as kerr:
			self.print_kw_error(kw)
			raise kerr
		self.history = np.zeros(len(self.bcoef))
		Module.__init__(self, *args, **kwargs)

	def process(self, signal):
		for n in xrange(0,len(signal)):
			self.history[0] = signal[n]
			signal[n] = np.sum(self.history * self.bcoef)
			self.history[1:] = self.history[0:-1]

