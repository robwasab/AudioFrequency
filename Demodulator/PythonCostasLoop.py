from   numpy import cos, sin, pi
from   LowPass import LowPass
import numpy as np

class PythonCostasLoop(object):
	def __init__(self, fc, fs=44.1E3, debug = False):
		self.fs = fs
		self.fc = fc
		self.F = fc/fs
		self.debug = debug
		self.vco_integrator = Integrator(self.F)
		
		# for estimating the frequency
		self.last_vco_phase = 0 

		# Special 2nd order integrator for tracking ramping phase
		self.phase_integrator = LoopIntegrator()

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
		self.lock_detect = LockDetect(fs, .01) 

		# State Variable
		self.lock = False

		self.rc_sig = 0
		self.rc_tau = 0.005
		self.gain = 1.0
		self.ref  = 1.0 
		self.step = 0.05
	
	def reset(self):
		self.vco_integrator.reset()
		self.last_vco_phase = 0
		self.phase_integrator.reset()
		self.ilp.reset()
		self.qlp.reset()
		self.ilp_signal.reset()
		self.qlp_signal.reset()
		self.freq_filter.reset()
		self.lock_detect.reset()
		self.lock = False

	def rc_filter(self, sig):
		self.rc_sig = (sig + self.rc_tau*self.fs*self.rc_sig)/(1+self.rc_tau*self.fs)
		return self.rc_sig	

	# Main work function
	def work(self, input):
		#loop_start = time()
		input *= self.gain
		if not self.lock:
			power = self.rc_filter(input**2)
			self.gain  = self.gain - self.step * (power - self.ref) * power/self.gain
		
		real_input = input

		# Hard Limit
		if input > 1:
			input = 1
		elif input < -1:
			input = -1

		# Phase Generator
		# vco_phase is a constantly increasing phase value
		# vco_phase = self.phase_integrator.value() + 2.0*pi*self.vco_integrator.value()	
		vco_phase = 2.0*pi*(self.phase_integrator.value() + self.vco_integrator.value())

		# Oscillator	
		cos_vco = cos(vco_phase)
		sin_vco =-sin(vco_phase)

		# Error Generator
		in_phase  = self.ilp.work(input * cos_vco)
		qu_phase  = self.qlp.work(input * sin_vco)

		# Update Loop Integrators
		self.phase_integrator.work(in_phase*qu_phase) 
		self.vco_integrator.work(1.0)

		# Downconvert analog
		in_phase_signal = 2.0*self.ilp_signal.work(real_input * cos_vco)

		qu_phase_signal = 2.0*self.qlp_signal.work(real_input * sin_vco)

		# Lock Detector
		lock = self.lock_detect.work(in_phase_signal, qu_phase_signal)

		if lock and not self.lock:
			print 'Locked..'
			print 'Autogain %f'%self.gain
			self.lock = True
	
		elif not lock and self.lock:
			print 'Unlocked..'
			self.lock = False
	
		if self.debug:
			# Frequency Est.
			self.freq_filter.work((vco_phase - self.last_vco_phase)*self.fs/(2.0*pi))
			self.last_vco_phase = vco_phase

			# Error Signal
			error = in_phase * qu_phase

			return (vco_phase, error, in_phase_signal, qu_phase_signal, cos_vco, sin_vco, self.freq_filter.y1, lock)
		else:
			#scale the signal back to the original size
			return in_phase_signal

class LockDetect(object):
	def __init__(self, fs, thresh = 1E-2):
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
	
	def reset(self):
		self.in_phase_lp.reset()
		self.qu_phase_lp.reset()

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
		self.last_s3 = self.k1*s1 + self.integrator1.work(s1*self.k1*self.k2+self.integrator2.work(s1*self.k1*self.k2*self.k3))
		return self.last_s3

	def value(self):
		return self.last_s3

	def reset(self):
		self.last_s3 = 0
		self.integrator1.reset()
		self.integrator2.reset()

class Integrator(object):
	def __init__(self, ki = 1):
		self.lasty = 0
		self.ki = ki
		self.lastx = 0

	def value(self):
		return self.lasty

	def work(self, input):
		self.lasty = self.ki*self.lastx + self.lasty
		self.lastx = input
		return self.lasty 
	
	def reset(self):
		self.lasty = 0
		self.lastx = 0

