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
		
	def reset(self):
		self.save = np.zeros(self.slen)

	def conv_chunk(self,sig,fsync_hack=False):
		size = self.chunklen - self.slen  # size sig chunk + slen = pwr of 2
		pad = [0] * (len(self.bcoef) - 1 + size - ((len(self.bcoef)+len(sig)-1)%size)) # pad make sig integer number of size
		sig = np.append(sig, pad)
		outp = []
		for k in range(0, len(sig)/size):
			self.save = np.append(self.save, sig[k*size:(k+1)*size])
			raw = peri_convo(self.save, self.bcoef)
			if fsync_hack:
				idx = np.argmax(raw)
				if raw[idx] > 0.75:
					return k * size + idx
			#print k, k*size, (k+1)*size
			outp.extend(raw[self.slen:].tolist())
			self.save = self.save[-self.slen:]
		if fsync_hack:
			return -1
		else:
			return outp[:len(sig)-len(pad)+self.slen]
