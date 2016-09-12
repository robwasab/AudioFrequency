from   Parent.Module import Module
from   numpy import cos, sin, pi
import numpy as np

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

	def process(self, data):
		if self.debug:
			self.phase = np.zeros(len(data))
			self.error = np.zeros(len(data))
		demod = np.zeros(len(data))
		for n in xrange(0, len(data)):
			if self.debug:
				phase, error, in_phase, qu_phase, in_vco, qu_vco = self.costa.work(data[n])
				demod[n] = in_phase 
				self.phase[n] = phase
				self.error[n] = error
			else:
				demod[n] = self.costa.work(data[n])
		if self.debug:
			if self.plt != None:
				self.plt.figure(self.fig)
				self.plt.gcf().clf()
				self.plt.plot(data)
				self.plt.plot(self.error)
				self.plt.show(block = False)
		return demod

class CostasLoop(object):
	def __init__(self, fc, fs=44.1E3, debug = False):
		self.fs = fs
		self.fc = fc
		self.F = fc/fs
		self.debug = debug
		self.vco_integrator = Integrator(2.0*pi*self.F)
		self.phase_integrator = Integrator()
		self.ilp = LowPass(fc, fs)
		self.qlp = LowPass(fc, fs)
		self.ilp_signal = LowPass(fc, fs)
		self.qlp_signal = LowPass(fc, fs)
		self.mu = 0.5 

	def work(self, input):
		real_input = input

		# Hardliner
		if input > 1:
			input = 1
		elif input < -1:
			input = -1

		vco_phase = self.phase_integrator.value() + self.vco_integrator.value()
		cos_vco   = cos(vco_phase)
		sin_vco   =-sin(vco_phase)
		cos_error = input * cos_vco
		sin_error = input * sin_vco
		in_phase  = self.ilp.work(cos_error)
		qu_phase  = self.qlp.work(sin_error)
		error = in_phase * qu_phase
		#error = cos_error * sin_error
		self.phase_integrator.work(error * self.mu) 
		self.vco_integrator.work(1.0 + error) 

		in_phase_signal = 2.0*self.ilp_signal.work(real_input * cos_vco)

		if self.debug:
			qu_phase_signal = 2.0*self.qlp_signal.work(real_input * sin_vco)
			return (self.phase_integrator.value(), error, in_phase_signal, qu_phase_signal, cos_vco, sin_vco)
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
