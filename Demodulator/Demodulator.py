from   Parent.Module import Module
from   numpy import cos, sin, pi
from   time import time
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
		self.loop_time = 0
	
	def process(self, data):
		if self.debug:
			self.phase = np.zeros(len(data))
			self.error = np.zeros(len(data))
			self.ipower = np.zeros(len(data))
			self.qpower = np.zeros(len(data))
			self.freqs  = np.zeros(len(data))
			self.locks  = np.zeros(len(data))

		demod = np.zeros(len(data))
		start = time()
		for n in xrange(0, len(data)):
			if self.debug:
				phase, error, in_phase, qu_phase, in_vco, qu_vco, freq, lock = self.costa.work(data[n])
				demod[n] = in_phase 
				self.phase[n] = phase
				self.error[n] = error
				self.qpower[n] = self.qp_lp.work(qu_phase**2)
				self.ipower[n] = self.ip_lp.work(in_phase**2)
				self.freqs[n]  = freq
				self.locks[n]  = lock
			else:
				demod[n] = self.costa.work(data[n])
		if self.debug:
			if self.plt != None:
				self.plt.figure(self.fig)
				self.plt.gcf().clf()
				plot_dc = 'plot_dc'
				plot_freq_phase = 'plot_freq_phase'
				plot_mode = plot_dc
				if plot_mode == plot_dc:
					self.plt.subplot(511)
					self.plt.plot(self.ipower, 'r')
					self.plt.title('In Phase')
					self.plt.subplot(512)
					self.plt.plot(self.qpower, 'b')
					self.plt.title('Quad Phase')
					self.plt.subplot(513)
					self.plt.plot(self.locks)
					self.plt.title('Locked')
					self.plt.subplot(514)
					self.plt.plot(demod)
					self.plt.title('Data')
					self.plt.subplot(515)
					self.plt.plot(self.freqs)
					self.plt.title('Frequencies')
				elif plot_mode == plot_freq_phase:
					self.plt.subplot(211)
					self.plt.plot(10.0*np.log10(self.phase))
					self.plt.title('Ramping Phase')
					self.plt.subplot(212)
					self.plt.plot(self.freqs)
					self.plt.title('Frequencies')

				self.plt.show(block = False)
			self.costa.print_times()
			print 'Average Loop time: %.3f'%(self.costa.time_loop*1E6)
		duration = time() - start
		avg_loop = duration / float(len(data))*1E6
		self.log('Avg Loop Duration:\t%.3f [us]'%avg_loop)
		self.log('%.3f Hz Sample Period:\t%.3f [us]'%(self.fs, 1E6/self.fs))
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
		self.lock_detect = CostasLoop.LockDetect(fs, 1E-3) 

		# State Variable
		self.lock = False

		# Timing Variables
		labels = ['time phase gen', 'time freq calc', 'time osc', 'time error', 'time integ', 'time analog', 'time lock']
		self.create_timers(labels)
		self.time_loop = 0.0
		
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
		def __init__(self, k1=1.0/3.0, k2=1.0/4.0, k3=1.0/16.0):
			self.k1 = k1
			self.k2 = k2
			self.k3 = k3
			self.integrator1 = Integrator()
			self.integrator2 = Integrator()
			self.last_s3 = 0

		def work(self, s1):
			s3 = self.k1*s1 + self.integrator1.work(s1*self.k1*self.k2+self.integrator2.work(s1*self.k1*self.k2*self.k3))
			self.last_s3 = s3
			return s3

		def value(self):
			return self.last_s3
	
	def create_timers(self, labels):
		self.times = np.zeros(len(labels), np.float)
		self.labels = labels
		self.current_timer = 0
	
	def print_times(self):
		total = 0.0
		for n in range(0, len(self.labels)):
			label = self.labels[n]
			delta = self.times[n]*1E6
			print '%s:\t%.3f [us]'%(label, delta)
			total+= delta
		print 'total:\t%.3f [us]'%total

	def tstart(self):
		self.time_start = time()
	
	def tstop(self):
		delta = time()-self.time_start
		self.times[self.current_timer] += delta
		self.times[self.current_timer] /= 2.0
		self.current_timer = (self.current_timer + 1)%len(self.times)

	# Main work function
	def work(self, input):
		#loop_start = time()

		real_input = input

		# Hard Limit
		if input > 1:
			input = 1
		elif input < -1:
			input = -1

		# Phase Generator
		# vco_phase is a constantly increasing phase value
		# vco_phase = self.phase_integrator.value() + 2.0*pi*self.vco_integrator.value()	
		#self.tstart()
		vco_phase = self.phase_integrator.value() + self.vco_integrator.value()
		#self.tstop()

		# Frequency Est.
		# self.freq_filter.work((vco_phase - self.last_vco_phase)/(2.0*pi)*self.fs)
		#self.tstart()
		#self.freq_filter.work((vco_phase - self.last_vco_phase)*self.fs)
		#self.last_vco_phase = vco_phase
		#self.tstop()

		# Oscillator	
		#self.tstart()
		vco_radians = 2.0*pi*vco_phase
		cos_vco = cos(vco_radians)
		sin_vco =-sin(vco_radians)
		#cos_vco = self.squ_cos(vco_phase)
		#sin_vco =-self.squ_sin(vco_phase)
		#self.tstop()

		# Error Generator
		#self.tstart()
		in_phase  = self.ilp.work(input * cos_vco)
		qu_phase  = self.qlp.work(input * sin_vco)
		error = in_phase * qu_phase
		#self.tstop()

		# Update Loop Integrators
		#self.tstart()
		self.phase_integrator.work(error) 
		self.vco_integrator.work(1.0)
		#self.tstop()

		# Downconvert analog
		#self.tstart()
		in_phase_signal = 2.0*self.ilp_signal.work(real_input * cos_vco)
		#qu_phase_signal = 2.0*self.qlp_signal.work(real_input * sin_vco)
		#self.tstop()

		# Lock Detector
		#self.tstart()
		#lock = self.lock_detect.work(in_phase_signal, qu_phase_signal)
		#self.tstop()

		#if self.lock != lock:
		#	self.lock = lock
		#	print 'Lock State: ' + str(lock)
		#	print 'frequency : %.3f'%self.freq_filter.y1
			#cycles = vco_phase/(2.0*pi)
			#print 'Cycles: %.3f'%cycles
		#	if lock:
		#		print 'vco_phase : %.3f'%vco_phase
		#		offset = (cycles - np.floor(cycles))*2.0*pi
		#		print 'est offset: %.3f'%offset
		#		print 'Locking Oscillator'
		#		self.locked_error = error 
		#	print ''
		#time_loop = time() - loop_start
		#self.time_loop += time_loop
		#self.time_loop /= 2.0

		if self.debug:
			return (vco_phase, error, in_phase_signal, qu_phase_signal, cos_vco, sin_vco, self.freq_filter.y1, lock)
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
