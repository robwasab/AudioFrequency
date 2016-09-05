from   Filter.FastFilter import FastFilter
import numpy as np
import pdb

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
		if index == -1:
			print self.FAIL + 'Could not find start index...' + self.ENDC
		print self.GREEN + 'Start Frame: %d'%index + self.ENDC
		self.reset()
		return data[index + 1:]
		#print idx
		#if idx >= 0:
		#	return data[idx+1:]
		#else:
		#	print self.FAIL + 'Could not find header...'
		#	return data
