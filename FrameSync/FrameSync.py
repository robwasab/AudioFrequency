from   Filter.FastFilter import FastFilter
from   Functions.util import quantize
from   struct import unpack
import numpy as np
import pdb

def pam2letters(pam):
	return ''.join(c for c in [chr(np.sum(quad << np.arange(len(quad)-1,-1,-1)*2)) for quad in np.reshape((np.array(pam)+3)/2,(len(pam)/4,4))])

class FrameSync(FastFilter):
	def __init__(self, *args, **kwargs):
		try:
			corr_prefix  = np.fliplr([kwargs['prefix']])[0]
			corr_prefix /= np.sum(corr_prefix**2)
			kwargs['bcoef'] = corr_prefix
			FastFilter.__init__(self, *args, **kwargs)

		except KeyError as ke:
			print self.FAIL + 'Key word argument \'prefix\' required' + self.ENDC
			raise(ke)

	def process(self, data):
		index, s = self.conv_chunk(data, fsync_hack = True)

		if index == -1:
			self.log('Not passing any more data')
			return None 

		self.log('Got a start index')

		# reset after you actually got a start index
		self.reset()
		payload = [quantize(d) for d in s*data[index + 1:]]

		num_bytes,= unpack('H', pam2letters(payload[:8]))

		self.log('num_bytes: %d'%num_bytes)
		num_bytes+= 1
		letters = pam2letters(payload[8:8+(4*num_bytes)])
		return letters
