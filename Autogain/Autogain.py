from Parent.Module import Module

class Autogain(Module):

	def __init__(self, *args, **kwargs):
		Module.__init__(self, *args, **kwargs)
		self.gain = 1.0
		self.step = 1E-4
		self.pwr  = 10

	def process(self, signal):
		for n in xrange(0,len(signal)):
			x = self.gain * signal[n]
			x_sq = x*x
			dy_dgain = (x_sq - self.pwr)*x_sq/self.gain
			self.gain -= self.step*dy_dgain
			signal[n] = x
		return signal
