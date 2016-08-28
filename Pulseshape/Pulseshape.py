from   Parent.Module import Module
from   scipy.signal import convolve, hamming
import numpy as np
from   numpy import sqrt, power, sin, cos, pi
import pdb


# Ported from MATLAB Software Receiver Design
def srrc(syms, beta, P, t_off = 0):
	# Generate a Square-Root Raised Cosine Pulse
	# 'syms' is 1/2 the length of srrc pulse in symbol durations
	# 'beta' is the rolloff factor: beta=0 gives the sinc function
	# 'P' is the oversampling factor
	# 't_off' is the phase (or timing) offset
	# sampling indices as a multiple of T/P
	k=np.arange(-syms*P+1e-8+t_off,syms*P+1e-8+t_off+1);           
	if beta == 0:
		beta=1e-8 # numerical problems if beta=0

	P = float(P)
	s = 4.0*beta/sqrt(P)*(cos((1.0+beta)*pi*k/P) + sin((1.0-beta)*pi*k/P) / (4.0*beta*k/P)) / (pi*(1.0-16.0*power(beta*k/P,2.0)))
	return s

class Pulseshape(Module):
	def __init__(self, *args, **kwargs):
		Module.__init__(self, *args, **kwargs)
		self.kwargs = kwargs
		
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

		self.M     = M
		self.ps    = ps
	
	def pulseshape(self, signal):
		mup = np.zeros(self.M*len(signal))
        	mup[np.arange(0,len(mup),self.M)] = signal	
		mup_analog = convolve(self.ps, mup)
		return mup_analog

	def process(self, data):
		analog_signal = self.pulseshape(data) 	

		if self.debug:
			self.plt.figure(self.fig)
			self.plt.subplot(211)
			self.plt.cla()
			self.plt.plot(analog_signal)

			self.plt.subplot(212)
			self.plt.cla()
			self.plt.stem(data)
			self.plt.xlim((-1, len(data) + 1))
			self.plt.ylim((-3.5, 3.5))

		return analog_signal
