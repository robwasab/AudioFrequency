from   Filter.FastFilter import FastFilter
from   scipy.signal import hamming
from   numpy import sqrt, power, sin, cos, pi
from   numpy.fft import fft, ifft
import numpy as np
import pdb

# Ported from MATLAB Software Receiver Design
def srrc(syms, beta, P, t_off = 0):
	k=np.arange(-syms*P+1e-8+t_off,syms*P+1e-8+t_off+1);           
	if beta == 0:
		beta=1e-8 # numerical problems if beta=0

	P = float(P)
	s = 4.0*beta/sqrt(P)*(cos((1.0+beta)*pi*k/P) + sin((1.0-beta)*pi*k/P) / (4.0*beta*k/P)) / (pi*(1.0-16.0*power(beta*k/P,2.0)))
	return s

class Pulseshape(FastFilter):
	def __init__(self, *args, **kwargs):
		M  = 101
		ps = hamming(M)
		
		#SRRC variables
		beta          = -1
		symbol_delay  =  3
		return_filter =  False

		for key in kwargs:
			if key == 'ps':
				ps = kwargs[key]
			elif key == 'beta':
				beta = float(kwargs[key])
			elif key == 'symbol_delay':
				symbol_delay = int(kwargs[key])
			elif key == 'return_filter' or key == 'return_ps':
				return_filter = True
			elif key == 'M':
				M = int(kwargs[key])
	
		if beta != -1:
			ps = srrc(symbol_delay, beta, M)

		self.M = M
		self.ps = ps
		kwargs['bcoef'] = ps
		FastFilter.__init__(self, *args, **kwargs)

	def process(self, signal):
		mup = np.zeros(self.M*len(signal))
        	mup[np.arange(0,len(mup),self.M)] = signal	
		analog_signal = FastFilter.process(self, mup)
		if self.debug:
			self.plt.figure(self.fig)
			self.plt.subplot(211)
			self.plt.cla()
			self.plt.plot(analog_signal)

			self.plt.subplot(212)
			self.plt.cla()
			self.plt.stem(signal)
			self.plt.xlim((-1, len(signal) + 1))
			self.plt.ylim((-3.5, 3.5))

		return analog_signal
