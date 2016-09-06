from   Parent.Module  import Module
from   Functions.util import quantize
import numpy as np

class TimingRecovery(Module):
	def __init__(self, *args, **kwargs):
		Module.__init__(self, *args, **kwargs)
		self.alphabet = [-3, -1, 1, 3]
		try:
			self.M = int(kwargs['M'])
		except KeyError as ke:
			print self.FAIL+'You must pass ' + str(ke) + ' as key word argument'
			raise ke

		self.offset = int(np.random.rand()*2*self.M)


	def process(self, data):
		down_samples = np.zeros(len(data)/self.M)
		down_samples_index = 1 
		step = self.M / 2		
		
		for skip_by_m in range(0, len(data), self.M):
			#print self.offset
			n = int(round(skip_by_m + self.offset))
			if n >= len(data):
				break
			down_samples[down_samples_index] = data[n]
			down_samples_index += 1
			if down_samples_index >= len(down_samples):
				break
			dy_doffset = (quantize(data[n], self.alphabet) - data[n]) * (data[n+1] - data[n-1])
			self.offset += step * dy_doffset

		#print self.BLUE + 'down_samples_index [%d/%d]'%(down_samples_index, len(data)/self.M)
		self.log('adaptation offset: %.3f'%self.offset)
		return down_samples[0:down_samples_index]
