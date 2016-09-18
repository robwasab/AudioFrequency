from   Parent.Module import Module
from   numpy import cos, sin, pi
import numpy as np

def fround(fc, fs):
	n = np.round(float(fs)/float(fc))
	return fs/n

class Demodulator(Module):
	def __init__(self, *args, **kwargs):
		Module.__init__(self, *args, **kwargs)
		self.fc = 11E3
		self.fs = 44.1E3
		for key in kwargs:
			if key == 'fc':
				self.fc = float(kwargs['fc'])
			elif key == 'fs':
				self.fs = float(kwargs['fs'])

		self.costa = CostasLoop(self.fc, self.fs, self.debug)
		self.ip_lp = LowPass(10, self.fs)
		self.qp_lp = LowPass(10, self.fs)
		self.fc = fround(self.fc, self.fs)
		self.log('fcenter: %.3f Hz'%self.fc)
	
	def process(self, data):
		if self.debug:
			self.phase = np.zeros(len(data))
			self.error = np.zeros(len(data))
			self.ipower = np.zeros(len(data))
			self.qpower = np.zeros(len(data))
			self.freqs  = np.zeros(len(data))

		demod = np.zeros(len(data))
		for n in xrange(0, len(data)):
			if self.debug:
				phase, error, in_phase, qu_phase, in_vco, qu_vco, freq = self.costa.work(data[n])
				demod[n] = in_phase 
				self.phase[n] = phase
				self.error[n] = error
				self.qpower[n] = self.qp_lp.work(qu_phase**2)
				self.ipower[n] = self.ip_lp.work(in_phase**2)
				self.freqs[n]  = freq
			else:
				demod[n] = self.costa.work(data[n])
		if self.debug:
			if self.plt != None:
				self.plt.figure(self.fig)
				self.plt.gcf().clf()
				self.plt.subplot(411)
				self.plt.plot(self.ipower, 'r')
				self.plt.title('In Phase')
				self.plt.subplot(412)
				self.plt.plot(self.qpower, 'b')
				self.plt.title('Quad Phase')
				self.plt.subplot(413)
				self.plt.plot(demod)
				self.plt.title('Data')
				self.plt.subplot(414)
				self.plt.plot(self.freqs)
				self.plt.title('Frequencies')
				self.plt.show(block = False)
		return demod

class CostasLoop(object):
	def __init__(self, fc, fs=44.1E3, debug = False):
		self.fs = fs
		self.fc = fc
		self.F = fc/fs
		self.debug = debug
		self.vco_integrator = Integrator(self.F)
		
		# for estimating the frequency
		self.last_vco_phase = 0 

		# Special 2nd order integrator for tracking ramping phase
		self.phase_integrator = CostasLoop.LoopIntegrator()

		# Low Pass filters for generating the error signal
		self.ilp = LowPass(fc, fs)
		self.qlp = LowPass(fc, fs)

		# Low Pass filters for filtering the output signal
		self.ilp_signal = LowPass(2E3 if fc > 2E3 else fc, fs)
		self.qlp_signal = LowPass(2E3 if fc > 2E3 else fc, fs)

		# Low Pass filter for estimating the frequency
		# By taking the phase difference of each vco iteration
		# And then passing it through this filter
		self.freq_filter = LowPass(100, fs)

		# Lock Detector. If the in phase power is above the 
		# Threshold and quadrature phase below the threshold,
		# Then it will report True for locked. 
		self.lock_detect = CostasLoop.LockDetect(fs, 1E-4) 

		# State Variable
		self.lock = False
		self.osc_lock = False
		
	class LockDetect(object):
		def __init__(self, fs, thresh = 1E-3):
			# Intentionally a ridiculously low frequency
			# Because we are basically trying to measure DC component
			self.in_phase_lp = LowPass(10, fs)
			self.qu_phase_lp = LowPass(10, fs)
			self.thresh = thresh 

		def work(self, in_phase, qu_phase):
			in_phase = self.in_phase_lp.work(in_phase**2)
			qu_phase = self.qu_phase_lp.work(qu_phase**2)
			if in_phase > self.thresh and qu_phase < self.thresh:
				return True
			return False

	# Values are determined experimentally by updating, running, and repeating
	class LoopIntegrator(object):
		def __init__(self, k1=2.0/3.0, k2=1.0/4.0, k3=1.0/16.0):
			self.k1 = k1
			self.k2 = k2
			self.k3 = k3
			self.integrator1 = Integrator()
			self.integrator2 = Integrator()
			self.last_s3 = 0

		def work(self, signal):
			s1 = signal
			s3 = self.k1*s1 + self.integrator1.work(s1*self.k1*self.k2+self.integrator2.work(s1*self.k1*self.k2*self.k3))
			self.last_s3 = s3
			return s3

		def value(self):
			return self.last_s3
		
	def generate_wavelet(self, vco_phase):
		fc = fround(self.freq_filter.y1, self.fs)
		print 'Generating Wavelet with fc = %.3f Hz'%fc
		offset = vco_phase - float(int(vco_phase/(2.0*pi)))
		n = int(self.fs/fc)
		phases = 2.0*pi*np.arange(n)/self.fs + offset
		self.cos_wavelet = cos(phases)
		self.sin_wavelet = sin(phases) 
		self.wavelet_ind = 1
		self.wavelet_n   = n
	
	def next_cos(self):
		val = self.cos_wavelet[self.wavelet_ind]	
		self.wavelet_ind = (self.wavelet_ind + 1) % self.wavelet_n
		return val

	def next_sin(self):
		val = self.sin_wavelet[self.wavelet_ind]	
		self.wavelet_ind = (self.wavelet_ind + 1) % self.wavelet_n
		return val
	
	# Main work function
	def work(self, input):
		real_input = input

		# Saturator, if the input rises beyond +/- will be
		# Thrown out of lock
		if input > 1:
			input = 1
		elif input < -1:
			input = -1
		
		# vco_phase is a constantly increasing phase value
		vco_phase = self.phase_integrator.value() + 2.0*pi*self.vco_integrator.value()	
		self.freq_filter.work((vco_phase - self.last_vco_phase)/(2.0*pi)*self.fs)
		self.last_vco_phase = vco_phase
		cos_vco = 0
		sin_vco = 0
		if not self.osc_lock:
			cos_vco = cos(vco_phase)
			sin_vco =-sin(vco_phase)

			#if self.lock:
			#	self.osc_lock = True
			#	self.generate_wavelet(vco_phase)
			#	print 'Oscillator Locked'
		else:
			cos_vco = self.next_cos()
			sin_vco =-self.next_sin()

		cos_error = input * cos_vco
		sin_error = input * sin_vco
		in_phase  = self.ilp.work(cos_error)
		qu_phase  = self.qlp.work(sin_error)

		lock = self.lock_detect.work(in_phase, qu_phase)

		#if self.lock != lock:
		#	self.lock = lock
		#	self.osc_lock = False
		#	print 'Lock State: ' + str(lock)

		error = in_phase * qu_phase
		
		if not self.lock:
			self.phase_integrator.work(error) 

		self.vco_integrator.work(1.0) 
		in_phase_signal = 2.0*self.ilp_signal.work(real_input * cos_vco)

		if self.debug:
			qu_phase_signal = 2.0*self.qlp_signal.work(real_input * sin_vco)
			return (self.phase_integrator.value(), error, in_phase_signal, qu_phase_signal, cos_vco, sin_vco, self.freq_filter.y1)
		else:
			return in_phase_signal

class Integrator(object):
	def __init__(self, ki = 1):
		self.lasty = 0
		self.ki = ki
		self.lastx = 0

	def value(self):
		return self.lasty

	def work(self, input):
		y = self.ki*self.lastx + self.lasty
		self.lasty = y
		self.lastx = input
		return y

class LowPass(object):
	def __init__(self, fc, fs, Q = 0.7071):
		#Biquad filter
		self.a0 = self.a1 = self.a2 = 0
		self.b0 = self.b1 = self.b2 = 0
		self.x1 = self.x2 = 0
		self.y1 = self.y2 = 0
		A = 1.0
		omega = 2.0*np.pi*fc/fs
		sn = np.sin(omega)
		cs = np.cos(omega)
		alpha = sn / (2.0*Q)
		beta  = np.sqrt(A+A)
		self.init_lp(A, omega, sn, cs, alpha, beta)
		self.b0 /= self.a0
		self.b1 /= self.a0
		self.b2 /= self.a0
		self.a1 /= self.a0
		self.a2 /= self.a0

	def init_lp(self, A, omega, sn, cs, alpha, beta):
		self.b0 = (1.0 - cs) / 2.0
		self.b1 =  1.0 - cs
		self.b2 = (1.0 - cs) / 2.0
		self.a0 =  1.0 + alpha
		self.a1 = -2.0 * cs
		self.a2 =  1.0 - alpha
	
	def work(self, x):
		y = self.b0 * x + self.b1 * self.x1 + self.b2 * self.x2 - self.a1 * self.y1 - self.a2 * self.y2
		self.x2, self.x1 = self.x1, x
		self.y2, self.y1 = self.y1, y
		return y
