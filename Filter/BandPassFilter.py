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
		kw = ''
		try:
			kw = 'fc'
			self.fc = kwargs[kw]
			kw = 'fs'
			self.fs = kwargs[kw]
			kw = 'bw'
			self.bw = kwargs[kw]
			kw = 'taps'
			self.taps = kwargs[kw]
			self.fir_lp = 2.0*signal.firwin(self.taps, self.bw/(self.fs/2.0))
			self.set_fc(self.fc)
			if self.box is not None:
				self.box_fc   = self.box.add_label('fc: %.1f'%self.fc)
				self.box_taps = self.box.add_label('taps: %d'%self.taps)

		except KeyError as ke:
			self.print_kw_error(kw)
			raise(ke)

	
	def process(self, audio):
		power = np.sum(audio**2)
		if power > 0.005:
			filtered = FastFilter.process(self, audio)
			if self.scope is not None:
				self.scope.set_fft(True)
				self.scope.set_fft_fs(44.1E3)
				self.scope.put(filtered)
			return filtered
			

	def set_fc(self, fc):
		bcoef = self.fir_lp * np.cos(2.0*np.pi*self.fc*np.arange(0,self.taps)/self.fs)
		self.set_bcoef(bcoef)
		if self.debug:
			resp = fft(bcoef)
			axis = np.arange(len(bcoef))/float(len(bcoef))*self.fs
			self.plt.plot(axis, np.abs(resp))
			self.plt.show()
	
