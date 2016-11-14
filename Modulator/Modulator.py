from Parent.Module import Module
import numpy as np

class Modulator(Module):
	def __init__(self, *args, **kwargs):
		Module.__init__(self, *args, **kwargs)
		kw = ''
		try:
			kw = 'fs'
			self.fs = float(kwargs['fs'])
			del kwargs['fs']

			kw = 'fc'
			self.fc = float(kwargs['fc'])
			self.osc_phase = Integrator(self.fc/self.fs)
			del kwargs['fc']

			self.offset = 0
			if kwargs.has_key('offset'):
				self.offset = float(kwargs['offset'])

			if self.box is not None:
				self.box_fc = self.box.add_label('fm: %.1f'%self.fc)

		except KeyError as ke:
			self.print_kw_error(kw)
			raise ke
	
	def reset(self):
		Module.reset(self)
		#self.incomplete = 0
		osc_phase.reset()

	def process(self, data):
		for n in xrange(len(data)):
			osc = 2.0*np.sin(2.0*np.pi*self.osc_phase.value())
			data[n] *= osc
			self.osc_phase.work(1.0)
		return data

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
