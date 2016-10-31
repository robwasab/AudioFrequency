from Parent.Module import Module
from time import time
import numpy as np

class Comparator(object):
	def __init__(self, thresh, high, low=0.0):
		self.thresh = thresh
		self.low = low
		self.high = high

	def work(self, input):
		return self.low if input>self.thresh else self.high

class LowPass(object):
	def __init__(self, tau, fs=44.1E3):
		self.tau = tau
		self.fs = fs
		self.rc_sig = 0

	def work(self, sig):
		self.rc_sig = (sig + self.tau*self.fs*self.rc_sig)/(1+self.tau*self.fs)
		return self.rc_sig	

	def reset(self):
		self.rc_sig = 0

class PeakDetect(LowPass):
	def __init__(self, *args):
		LowPass.__init__(self, *args)
	
	def work(self, sig):
		if np.abs(sig) > self.rc_sig:
			self.rc_sig = np.abs(sig)
			return self.rc_sig
		return LowPass.work(self, sig)

class Autogain(Module):
	def __init__(self, *args, **kwargs):
		Module.__init__(self, *args, **kwargs)
		fs = 44.1E3
		M = kwargs['M'] 
		self.gain = 30.0
		peak_tau  = M*200.0/fs
		lowp_tau  = M*400.0/fs
		self.peak = PeakDetect(peak_tau, fs)
		self.comp = Comparator(1.0, self.gain, 0.0)
		self.lowp = LowPass(lowp_tau, fs)
		self.init = time()
		self.timeout = 10.0
		self.rssi = 0
		
	def process(self, data):
		if time() > self.init + self.timeout:
			self.peak.reset()
			self.lowp.reset()
			self.log('resetting...')

		if self.debug and self.plt is not None:
			self.peaks = np.zeros(len(data))
			self.compa = np.zeros(len(data))
			self.lowpa = np.zeros(len(data))

		for n in xrange(len(data)):
			recv = self.gain*data[n]
			peak = self.peak.work(recv)
			self.rssi = peak
			comp = self.comp.work(peak)
			lowp = self.lowp.work(comp)
			self.gain = lowp
			data[n] = recv
			if self.debug and self.plt is not None:
				self.peaks[n] = peak
				self.compa[n] = comp
				self.lowpa[n] = lowp

		if self.debug and self.plt is not None:
			self.plt.figure(self.fig)
			self.plt.gcf().clf()
			self.plt.subplot(411)
			self.plt.plot(data)
			self.plt.title('data')

			self.plt.subplot(412)
			self.plt.plot(self.peaks)
			self.plt.title('peaks')

			self.plt.subplot(413)
			self.plt.plot(self.compa)
			self.plt.title('compa')
			self.plt.gca().set_ylim((-1,6))

			self.plt.subplot(414)
			self.plt.plot(self.lowpa)
			self.plt.title('low pass')

			self.plt.show()
		self.log('gain: %f'%self.gain)
		self.log('rssi: %f'%self.rssi)
		self.blog('gain: %.3f'%self.gain)
		self.blog('rssi: %.3f'%self.rssi)

		self.init = time()
		return data/2.0
