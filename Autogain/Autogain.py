from sys import float_info
from Parent.Module import Module
import numpy as np

class Autogain(Module):

	def __init__(self, *args, **kwargs):
		Module.__init__(self, *args, **kwargs)
		self.gain = 1.0
		self.step = 1E-4
		self.pwrs = [1, 9]
		self.hist = np.zeros(5)
	
	def error(self, input_pwr):
		min_error = float_info.max 
		ref_pwr = -1
		for pwr in self.pwrs:
			error = input_pwr - pwr 	
			if np.abs(error) < min_error:
				min_error = error
				ref_pwr = pwr
		return min_error, ref_pwr
		

	def process(self, signal):
		if self.debug:
			self.powers = np.zeros(len(signal))
			self.quanti = np.zeros(len(signal))
			self.gains  = np.zeros(len(signal))
			self.errors = np.zeros(len(signal))
			matlab = '['
			for s in signal:
				matlab += '%f,'%s
			matlab += ']'
			self.log(matlab)

		for n in xrange(0,len(signal)):
			x = self.gain * signal[n]
			signal[n] = x
			self.hist[1:] = self.hist[0:-1]
			self.hist[0] = x
			pwr = np.sum(self.hist**2)/float(len(self.hist))
			print pwr
			error, ref_pwr = self.error(pwr)
			if error > 20:
				break
			dy_dgain = 1000.0*error*pwr/self.gain
			self.gain -= self.step*dy_dgain
			if self.debug:
				self.powers[n] = pwr 
				self.gains[n]  = self.gain
				self.errors[n] = error
				self.quanti[n] = ref_pwr
		if self.debug and self.plt is not None:
			self.plt.figure(self.fig)
			self.plt.gcf().clf()
			self.plt.subplot(411)
			self.plt.plot(self.powers)
			self.plt.title('Autogain Power')
			self.plt.subplot(412)
			self.plt.plot(self.quanti)
			self.plt.title('Reference Powers')
			self.plt.ylim(0,10)
			self.plt.subplot(413)
			self.plt.plot(self.gains)
			self.plt.title('Gains')
			self.plt.subplot(414)
			self.plt.plot(self.errors)
			self.plt.title('Errors')
			self.plt.show(block=False)
		return signal
