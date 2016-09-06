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
			self.prefix  = np.fliplr([kwargs['prefix']])[0]
			self.prefix /= float(len(self.prefix))
			kwargs['bcoef'] = self.prefix
			FastFilter.__init__(self, *args, **kwargs)
		except KeyError as ke:
			print self.FAIL + 'Key word argument \'prefix\' required' + self.ENDC
			raise(ke)
	
	def process(self, data):
		index = self.conv_chunk(data, fsync_hack = True)
		self.reset()
		if index == -1:
			print self.FAIL + 'Could not find start index...' + self.ENDC
			return data
		
		payload = [quantize(d) for d in data[index + 1:]]
		
		# Beastly one-liner
		num_bytes,= unpack('H', pam2letters(payload[:8]))
		num_bytes+= 1
		return pam2letters(payload[8:8+(4*num_bytes)])

