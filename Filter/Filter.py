from   Parent.Module import Module
import numpy as np

class FirFilter(Module):
	def __init__(self, *args, **kwargs):
		Module.__init__(self, *args, **kwargs)
		try:
			self.bcoef = kwargs['bcoef']
		except KeyError as kerr:
			print Module.FAIL + self.__class__.__name__ + ' requires key word argument bcoef!' + Module.ENDC
			raise kerr

		self.history = np.zeros(len(self.bcoef))

	def process(self, signal):
		for n in xrange(0,len(signal)):
			self.history[0] = signal[n]
			signal[n] = np.sum(self.history * self.bcoef)
			self.history[1:] = self.history[0:-1]

