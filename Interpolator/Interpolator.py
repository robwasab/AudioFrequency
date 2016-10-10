from   Filter.FastFilter import FastFilter
from   scipy.signal import firwin
import numpy as np

class Interpolator(FastFilter):
	def __init__(self, *args, **kwargs):
		kw = ''
		try:
			kw = 'numtaps'
			self.numtaps = kwargs[kw]
			kw = 'L'
			self.L = int(kwargs[kw])
			kwargs['bcoef'] = firwin(self.numtaps, 1.0/self.L)
			kwargs['flush'] = False
			FastFilter.__init__(self, *args, **kwargs)
		except KeyError:
			self.print_kw_error(kw)
	
	def process(self, data):
		zero_pad = np.zeros(self.L*len(data))
		zero_pad[np.arange(len(data))*self.L] = data
		zero_pad *= self.L
		interpolated = FastFilter.conv_chunk_chunk(self, zero_pad)
		if self.debug:
			self.plt.figure(self.fig)
			self.plt.subplot(311)
			self.plt.plot(data)
			self.plt.subplot(312)
			self.plt.plot(zero_pad)
			self.plt.subplot(313)
			self.plt.plot(interpolated)
			self.plt.show(block = False)
		return interpolated

