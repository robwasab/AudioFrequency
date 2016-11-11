from   Pulseshape.Pulseshape import Pulseshape
from   FrameSync.FrameSync   import FrameSync
from   Filter.FastFilter     import FastFilter
# toeplitz is for equalizer algorithm
from   scipy.linalg import toeplitz
from   Queue import Empty, Full
# inv is for inverting a matrix in the equalizer
from   numpy.linalg import inv
from   numpy.fft import fft
from   time import time
import numpy as np
import pdb

class Equalizer(FastFilter):
	def __init__(self, *args, **kwargs):
		kw = ''
		try:
			kw = 'prefix'
			corr_prefix  = np.fliplr([kwargs[kw]])[0]

			# M = Decimation factor
			self.M = 4
			dec_corr_prefix = corr_prefix[np.arange(0, len(corr_prefix), self.M)]
			dec_corr_prefix_power = np.sum(dec_corr_prefix**2)
			dec_corr_prefix /= dec_corr_prefix_power

			# Samples to skip on the beginning of process when finding the header
			self.skip = 0

			kwargs['bcoef'] = dec_corr_prefix
			FastFilter.__init__(self, *args, **kwargs)

			self.buffer= np.zeros(len(corr_prefix))
			self.tail  = 0

			self.delay = 3 
			self.eqlen = 21 
			self.train = kwargs[kw][self.eqlen-1-self.delay:-self.delay]
			self.default_eq = np.zeros(self.eqlen)
			self.default_eq[0] = 1.0
		
			self.equal = FastFilter(bcoef = self.default_eq, flush=False)
			self.chan_resp = None
			self.sign = 1
			self.thresh = 0.75

		except KeyError as ke:
			self.print_kw_error(kw)
			raise(ke)

		for kw in kwargs:
			if kw == 'channel':
				channel = kwargs[kw]
				pad = np.zeros(2**8-len(channel))
				channel = np.append(channel, pad)
				self.chan_resp = np.abs(fft(channel))
		if self.debug:
			if self.plt != None:
				self.plt.figure(self.fig)
				self.plt.gcf().clf()
				self.plt.plot(self.train)
				self.plt.title('Initializiation: Equalizer Training Header')
				self.plt.show(block = False)

			self.eq_plt = None
			self.xaxis  = None
			N = 8 
			num = 2**N
			self.pad = np.zeros(num-self.eqlen)
			self.xaxis = np.arange(num)/float(num)

		if self.box is not None:
			self.box_max_equal_time  = self.box.add_label('max equal [ms]: 0')
			self.box_max_solve_time  = self.box.add_label('max solve [ms]: 0')
			self.box_max_corre_time  = self.box.add_label('max corre [ms]: 0')
		self.max_equal_time = 0
		self.max_solve_time = 0
		self.max_corre_time = 0
	
	def put(self, data):
		indexes = (self.tail+np.arange(len(data)))%len(self.buffer)
		self.tail = (self.tail + len(data))%len(self.buffer)
		self.buffer[indexes] = data

	def read_all(self):
		indexes = np.arange(self.tail-len(self.buffer), self.tail)%len(self.buffer)
		return self.buffer[indexes]


	def process(self, data):
		start = time()
		decimate_indecies = np.arange(self.skip, len(data), self.M) 
		index, s = self.conv_chunk_chunk(data[decimate_indecies], fsync_hack=True, flush=False, scope=self.scope)
		self.skip = (self.M - ((len(data)-self.skip) % self.M))%self.M
		stop = time()
		corre_time = stop-start

		if index == -1 :
			self.put(data)
			# TODO: CONTROLLER RESETS EQUALIZER COEFFICIENTS AFTER:
			# 1. Successful reception
			# 2. Timeout
			# 3. Error of some sort
			start = time()
			ret = self.equal.conv_chunk_chunk(data, fsync_hack=False, flush=False)
			stop = time()
			equal_time = stop-start
			if self.box is not None:
				if corre_time > self.max_corre_time:
					self.max_corre_time = corre_time
				if equal_time > self.max_equal_time:
					self.max_equal_time = equal_time
				
				self.box.notify(self.box_max_corre_time, 'max corre [ms]: %.3f'%(1000.0*self.max_corre_time))
				self.box.notify(self.box_max_equal_time, 'max equal [ms]: %.3f'%(1000.0*self.max_equal_time))
			return ret

		# so, if the sign is found to be -1, it means all of the data we have been previously filtering
		# is inversed
		# the equalizer will thus try to invert the data, which we get back
		# if we multiply the fir coefficients by the -1, we retain the previous state of the filter
		index = self.skip + index*self.M

		self.put(data[:index])
		self.log('FOUND TRAINING HEADER!')

		if self.debug:
			self.log('index: %d'%index)

		start = time()
		fir = self.equalizer(self.read_all()).tolist()
		self.equal.set_bcoef(s*np.array(fir))
		stop = time()
		solve_time = stop-start

		start = time()
		equalized_header = self.equal.conv_chunk_chunk(data, fsync_hack=False, flush=False)	
		stop = time()
		equal_time = stop-start

		if solve_time > self.max_solve_time:
			self.max_solve_time = solve_time

		if self.box is not None:
			self.max_corre_time = corre_time
			self.max_equal_time = equal_time
			self.box.notify(self.box_max_corre_time, 'max corre [ms]: %.3f'%(1000.0*self.max_corre_time))
			self.box.notify(self.box_max_solve_time, 'max solve [ms]: %.3f'%(1000.0*self.max_solve_time))
			self.box.notify(self.box_max_equal_time, 'max equal [ms]: %.3f'%(1000.0*self.max_equal_time))
		self.reset() 
		return equalized_header

	def equalizer(self, r):
		toe_row = r[-len(self.train):]
		toe_col = r[-len(self.train)-self.eqlen:-len(self.train)]
		R = np.matrix(toeplitz(toe_row, toe_col))
		S = np.matrix(self.train).getT()
		fir = inv(R.getT()*R)*R.getT()*S
		Jmin = (S.getT()*S-S.getT()*R*fir)[0,0]
		if self.debug:
			self.log('Delay: %d, Jmin: %f'%(self.delay, Jmin))
		if self.debug:
			freq_resp = np.abs(fft(np.append(fir.tolist(),self.pad)))
			if self.eq_plt == None:
				self.plt.figure(self.fig)
				self.plt.gcf().clf()
				#self.eq_plt, = self.plt.plot(self.xaxis, freq_resp)
				self.plt.plot(self.xaxis, freq_resp)
				if self.chan_resp is None:
					self.plt.plot(self.xaxis, self.chan_resp, 'r-')
				self.plt.title('Equalizer Response')
				self.plt.show(block=False)
			else:
				self.eq_plt.set_ydata(freq_resp)
				self.plt.figure(self.fig)
				self.plt.gcf().canvas.draw()
		return fir

	def dim(self, m):
		self.log('rows: %d\ncols: %d'%(len(m[:,0]), len(m[0,:])))
	
