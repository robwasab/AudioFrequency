from   Filter.FastFilter import FastFilter
from   Functions.util    import quantize
from   Whitener.Whitener import Whitener
from   struct import unpack
import numpy as np
import pdb


class FrameSync(FastFilter):
	def __init__(self, *args, **kwargs):
		kw = ''
		try:
			kw = 'prefix'
			corr_prefix  = np.fliplr([kwargs[kw]])[0].astype(float)
			corr_prefix /= np.sum(corr_prefix**2)
				

			kwargs['bcoef'] = corr_prefix
			FastFilter.__init__(self, *args, **kwargs)

			kw = 'cipher'
			self.cipher = kwargs[kw]

		except KeyError as ke:
			self.print_kw_error(kw)
			raise(ke)

		self.whiten = Whitener(cipher = self.cipher)


	def pam2num(self, pam):
		return [n for n in [np.sum(quad << np.arange(len(quad)-1,-1,-1)*2) for quad in np.reshape((np.array(pam)+3)/2,(len(pam)/4,4))]]

	def num2text(self, num):
		return ''.join([chr(b) for b in num])

	def process(self, data):
		index, s = self.conv_chunk(data, fsync_hack = True, debug = False)

		if index == -1:
			self.log('Not passing any more data')
			return None 

		self.log('Got a start index')
		self.log('index: %d'%index)

		# reset after you actually got a start index
		self.reset()

		# reset the whitener here, before you use it
		self.whiten.reset()

		#if self.debug and self.plt is not None:
		#	self.plt.figure(self.fig)
		#	self.plt.gcf().clf()
		#	self.plt.stem(data[index+1:])
		#	self.plt.title('PAM Data')
		#	self.plt.show(block=True)

		if self.debug and self.plt is not None:
			self.plt.figure(self.fig)
			self.plt.gcf().clf()
			self.plt.stem(data[index+1:])
			self.plt.title('Frame Sync: Data Header Removed')
			self.plt.show(block=False)

		payload = [quantize(d) for d in s*data[index + 1:]]
		self.log('full scrambled payload : ' + str(payload))
		num_bytes = self.whiten.process(self.pam2num(payload[:8]))
		num_bytes = (num_bytes[1] << 8) + num_bytes[0]	+ 1
		self.log('num_bytes: %d'%num_bytes)

		if num_bytes > (len(payload) - 8):
			self.log('num bytes is larger than available data, error')
			return None

		payload = payload[8:8+(num_bytes*4)]
		self.log('payload before whitening: ' + str(payload))
		payload = self.whiten.process(self.pam2num(payload))
		self.log('payload after  whitening: ' + str(payload))
		text = self.num2text(payload)	
		return text 
