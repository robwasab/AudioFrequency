from   Parent.Module import Module
from   sys import float_info
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

		self.offset = self.M/2

	def quantize(self, x):
		least_error = float_info.max
		closest = self.alphabet[0]

		for letter in self.alphabet:
			error = letter - x
			error*= error
			if error < least_error:
				closest = letter
				least_error = error
		return closest

	def process(self, data):
		down_samples = np.zeros(len(data)/self.M)
		down_samples_index = 0
		step = self.M		

		for skip_by_m in range(0, len(data), self.M):
			n = int(round(skip_by_m + self.offset))
			down_samples[down_samples_index] = data[n]
			down_samples_index += 1
			if down_samples_index >= len(down_samples):
				break
			dy_doffset = (self.quantize(data[n]) - data[n]) * (data[n+1] - data[n-1])
			self.offset += step * dy_doffset

		print self.BLUE + 'down_samples_index [%d/%d]'%(down_samples_index, len(data)/self.M)
		return down_samples[0:down_samples_index]
