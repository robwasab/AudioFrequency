from   Pulseshape.Pulseshape import Pulseshape
from   FrameSync.FrameSync   import FrameSync
from   Filter.FastFilter     import FastFilter
# toeplitz is for equalizer algorithm
from   scipy.linalg import toeplitz
# inv is for inverting a matrix in the equalizer
from   numpy.linalg import inv
from   numpy.fft import fft
import numpy as np

class Equalizer(FrameSync):
	def __init__(self, *args, **kwargs):
		FrameSync.__init__(self, *args, **kwargs)
		self.delay = 3 
		self.eqlen = 21 
		self.train = kwargs['prefix'][self.eqlen-1-self.delay:-self.delay]
		default_eq = np.zeros(self.eqlen)
		default_eq[0] = 1.0
		self.equal = FastFilter(bcoef = default_eq)
		self.chan_resp = None
		for kw in kwargs:
			if kw == 'channel':
				channel = kwargs[kw]
				pad = np.zeros(2**8-len(channel))
				channel = np.append(channel, pad)
				self.chan_resp = np.abs(fft(channel))
		if self.debug:
			self.eq_plt = None
			self.xaxis  = None
			N = 8 
			num = 2**N
			self.pad = np.zeros(num-self.eqlen)
			self.xaxis = np.arange(num)/float(num)
			

	def process(self, data):
		index, s = self.conv_chunk(data, fsync_hack=True, debug=False)
		if index == -1:
			self.log('Could not find start index')
			return None
		self.reset()
		fir = self.equalizer(data[:index]).tolist()
		self.equal.set_bcoef(fir)
		self.equal.reset()
		return self.equal.conv_chunk(data)	

	def equalizer(self, r):
		toe_row = r[-len(self.train):]
		toe_col = r[-len(self.train)-self.eqlen:-len(self.train)]
		R = np.matrix(toeplitz(toe_row, toe_col))
		S = np.matrix(self.train).getT()
		fir = inv(R.getT()*R)*R.getT()*S
		Jmin = (S.getT()*S-S.getT()*R*fir)[0,0]
		self.log('Delay: %d, Jmin: %f'%(self.delay, Jmin))
		if self.debug:
			freq_resp = np.abs(fft(np.append(fir.tolist(),self.pad)))
			if self.eq_plt == None:
				self.plt.figure(self.fig)
				self.plt.gcf().clf()
				#self.eq_plt, = self.plt.plot(self.xaxis, freq_resp)
				self.plt.plot(self.xaxis, freq_resp)
				if self.chan_resp != None:
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
