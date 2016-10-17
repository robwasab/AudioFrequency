from   FastFilter import FastFilter
import numpy as np
from   scipy import signal
from   numpy.fft import fft
#import matplotlib.pyplot as plt
#size = 2**10
#buffer = np.zeros(size)
#freqs = np.arange(size)/float(size)*44.1E3
#ax = plt.subplot(111)
#handle, = ax.plot(freqs, buffer)
#ax.set_xlim((freqs[0], freqs[-1]))
#ax.set_ylim((0, 1.0))
#plt.show(block = False)

class BandPassFilter(FastFilter):
	def __init__(self, *args, **kwargs):
		# Dummy 'bcoef'
		kwargs['bcoef'] = [1.0]
		FastFilter.__init__(self, *args, **kwargs)
		self.taps = 128
		kw = ''
		try:
			kw = 'fc'
			self.fc = kwargs[kw]
			kw = 'fs'
			self.fs = kwargs[kw]
			for kw in kwargs:
				if kw == 'taps':
					self.taps = kwargs[kw]
		except KeyError as ke:
			self.print_kw_error(kw)
			raise(ke)

		self.fir_lp = 2.0*signal.firwin(self.taps, 3E3/(self.fs/2.0))
		self.set_fc(self.fc)
	
	def process(self, audio):
		power = np.sum(audio**2)
		if power > 0.05:
			return FastFilter.process(self, audio)

	def set_fc(self, fc):
		bcoef = self.fir_lp * np.cos(2.0*np.pi*self.fc*np.arange(0,self.taps)/self.fs)
		self.set_bcoef(bcoef)
		if self.debug:
			resp = fft(bcoef)
			axis = np.arange(len(bcoef))/float(len(bcoef))*self.fs
			self.plt.plot(axis, np.abs(resp))
			self.plt.show()
	
