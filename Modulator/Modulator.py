from Parent.Module import Module
import matplotlib.pyplot as plt
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
			fc = float(kwargs['fc'])
			self.n  = int(np.round(self.fs/fc))
			self.fc = self.fs/self.n
			#self.log('User fc: %.3f -> %.3f'%(fc,self.fc))
			del kwargs['fc']

			self.offset = 0
			if kwargs.has_key('offset'):
				self.offset = float(kwargs['offset'])

		except KeyError as ke:
			self.print_kw_error(kw)
			raise ke
	
		w  = 2.0 * np.pi * self.fc
		ns = np.arange(0, int(self.n))
		fs = self.fs

		self.wavelet = np.sin(w*ns/self.fs)	
		self.incomplete = 0

		if self.debug:
			self.log('fs: %f'%self.fs)
			self.log('fc: %f'%self.fc)
			#plt.stem(self.wavelet)
			#plt.show(block = False)
	
	def reset(self):
		Module.reset(self)
		self.incomplete = 0

	
	def process(self, data):
		if self.incomplete > 0:
			if self.incomplete > len(data):
				offset = self.n - self.incomplete
				data[0:] = data[0:]*self.wavelet[offset:offset+len(data)]
				self.incomplete -= len(data)

				if self.debug:
					self.log('incomplete   : %d'%self.incomplete)
					self.log('wavelet size : %d'%self.n)
				return data
			else:
				data[0:self.incomplete] = data[0:self.incomplete] * self.wavelet[-self.incomplete:]

		for k in xrange(self.incomplete,len(data),self.n):
			if k+self.n > len(data):
				leftover = len(data)-k
				if self.debug:
					self.log('leftover     : %d'%leftover)

				data[k:k+leftover] *= self.wavelet[:leftover]

				self.incomplete = self.n - leftover 
				if self.debug:
					self.log('incomplete   : %d'%self.incomplete)
					self.log('wavelet size : %d'%self.n)
			else:
				data[k:k+self.n] *= self.wavelet
		return data


