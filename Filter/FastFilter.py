from   numpy.fft import ifft, fft
from   Filter import FirFilter
import numpy as np
import pdb

def peri_convo(sig,fir):
	delta = len(sig) - len(fir)
	if delta > 0:
		fir = np.append(fir, [0] * delta)
		sig = sig 
	elif delta < 0:
		sig = np.append(sig, [0] * -delta)
		fir = fir
	fftsig = fft(sig)
	fftfir = fft(fir)
	fftout = fftsig * fftfir
	out = ifft(fftout).real
	return out

class FastFilter(FirFilter):
	def __init__(self, *args, **kwargs):
		FirFilter.__init__(self, *args, **kwargs)
		self.slen = len(self.bcoef) - 1
		self.save = np.zeros(self.slen)
		self.chunklen = 128
		while self.chunklen < len(self.bcoef):
			self.chunklen *= 2

	def process(self, signal):
		outp = self.conv_chunk(signal)
		delta = self.slen - len(signal)
		if delta > 0:
			self.save = ([0] * delta).extend(signal) 
		else:
			self.save = signal[-self.slen]
		return outp[:len(signal)]
		
	def conv_chunk(self,sig,db=False):
		size = self.chunklen - self.slen  # size sig chunk + slen = pwr of 2
		pad = [0] * (len(self.bcoef) - 1 + size - ((len(self.bcoef)+len(sig)-1)%size)) # pad make sig integer number of size
		sig = np.append(sig, pad)
		outp = []
		for k in range(0, len(sig)/size):
			self.save = np.append(self.save, sig[k*size:(k+1)*size])
			if db:
				plt.clf()
				plt.subplot(211)
				plt.plot(save)
				plt.plot(save[0:slen], 'r.')
				plt.title('saved + signal chunk')
			raw = peri_convo(self.save, self.bcoef)
			if db:
				plt.subplot(212)
				plt.plot(raw)
				if len(outp) > len(fir):
					plt.plot(outp[-slen:], 'g')
				plt.title('convolution with (saved + signal chunk) and tri')
				plt.show(block=False)
				plt.pause(.1)
			#print k, k*size, (k+1)*size
			outp.extend(raw[self.slen:].tolist())
			self.save = self.save[-self.slen:]
		return outp[:len(sig)-len(pad)+self.slen]
