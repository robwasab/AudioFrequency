from   PythonCostasLoop import PythonCostasLoop as CostasLoop
from   Parent.Module import Module
from   LowPass import LowPass
from   time import time
import CostasLoopC
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

		CostasLoopC.init(self.fc, self.fs)
		self.costa = CostasLoop(self.fc, self.fs, self.debug)
		if self.debug:
			self.ip_lp = LowPass(10, self.fs)
			self.qp_lp = LowPass(10, self.fs)
	
		#self.fc = fround(self.fc, self.fs)
		#self.log('fcenter: %.3f Hz'%self.fc)
		self.loop_time = 0
	
	def process(self, data):
		return self.C_process(data)
	
	def C_process(self, data):
		start = time()
		ret = CostasLoopC.process(np.array(data, dtype=np.float32))
		duration = time() - start
		avg_loop = duration / float(len(data))*1E6
		self.log('Avg Loop time: %.3f [us]'%avg_loop)
		self.log('Time to beat : %.3f [us]'%(1E6/self.fs))
		return ret 

	def Python_process(self, data):
		if self.debug:
			self.phase = np.zeros(len(data))
			self.error = np.zeros(len(data))
			self.ipower = np.zeros(len(data))
			self.qpower = np.zeros(len(data))
			self.freqs  = np.zeros(len(data))
			self.locks  = np.zeros(len(data))

		start = time()
		for n in xrange(0, len(data)):
			if self.debug:
				phase, error, in_phase, qu_phase, in_vco, qu_vco, freq, lock = self.costa.work(data[n])
				data[n] = in_phase 
				self.phase[n] = phase
				self.error[n] = error
				self.qpower[n] = self.qp_lp.work(qu_phase**2)
				self.ipower[n] = self.ip_lp.work(in_phase**2)
				self.freqs[n]  = freq
				self.locks[n]  = lock
			else:
				data[n] = self.costa.work(data[n])
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
					self.plt.plot(data)
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

		duration = time() - start
		avg_loop = duration / float(len(data))*1E6
		self.log('Avg Loop time: %.3f [us]'%avg_loop)
		self.log('Time to beat : %.3f [us]'%(1E6/self.fs))
		self.costa.reset()
		return data
