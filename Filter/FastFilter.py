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

		# for good measure
		self.chunklen *= 2

	def process(self, signal):
		#self.log('input signal length: %6d'%len(signal))
		outp = self.conv_chunk(signal)
		#self.log('outpu signal length: %6d'%len(outp))
		delta = self.slen - len(signal)
		if delta > 0:
			self.save = ([0] * delta).extend(signal) 
		else:
			self.save = signal[-self.slen:]
		return outp
		
	def reset(self):
		self.save = np.zeros(self.slen)

	def conv_chunk(self,sig,fsync_hack=False):
		size = self.chunklen - self.slen  # size sig chunk + slen = pwr of 2
		pad  = [0] * (len(self.bcoef) - 1 + size - ((len(self.bcoef)+len(sig)-1)%size)) # pad make sig integer number of size
		sig  = np.append(sig, pad)
		outp = []
		ncyc = len(sig)/size
		#save_handle = None
		#raw_handle = None
		
		for k in range(0, ncyc):
		#	if not fsync_hack:
		#		self.log('[%d/%d]:'%(k,ncyc))
		#		self.log('        type(self.save ): ' + str(type(self.save)))
		#		self.log('        type(self.bcoef): ' + str(type(self.bcoef)))
		#		self.log('        save  length %d'%len(self.save))
		#		self.log('        bcoef length %d'%len(self.bcoef))
			self.save = np.append(self.save, sig[k*size:(k+1)*size])
			raw = peri_convo(self.save, self.bcoef)

			#self.plt.subplot(211)
			#if save_handle == None:
			#	save_handle, = self.plt.plot(self.save)
			#	self.plt.title('save')
			#	self.plt.ylim((-1.5,1.5))
			#else:
			#	save_handle.set_ydata(self.save)

			#self.plt.subplot(212)
			#if raw_handle == None:
			#	raw_handle, = self.plt.plot(raw)
			#	self.plt.title('raw')
			#	self.plt.ylim((-1.5, 1.5))
			#	self.plt.show(block = False)
			#else:
			#	raw_handle.set_ydata(raw)

			#self.plt.gcf().canvas.draw()
			#self.plt.pause(0.5)

			if fsync_hack:
				idx = np.argmax(np.abs(raw))
				# OK, this is pretty weird, it fucked my brain pretty hard.
				# It is where the maximimum correlation point happens in the
				# recorded data.
				# At first hand, I thought it would happen once an entire
				# prefix frame was captured.
				# But the peak will actually point to the index at the first
				# received data point of the prefix. This happens, because
				# prefix data exists at the end of the receive buffer. But,
				# because I am using FFT correlation, the correlation is 
				# wraping around.. haha, its really hard to explain, but with
				# that clue, if you ever have to understand it, will help you.
				if raw[idx] > 0.75: 
					# idx points to the 'last' point of the prefix, but it
					# is wrapped around the receive buffer
					
					# I did have to do a little guess work here, but the 
					# above analysis made me less blind, it really helped.
					start_idx = k*size + len(raw) + idx - self.slen
					sign = np.sign(raw[idx])
					self.log('Sign of correlation:')
					self.log(np.sign(raw[idx]))
					return (start_idx, sign)
			#else:
			#	self.log('[%d/%d] raw len: %d slen: %d'%(k,len(sig)/size, len(raw), self.slen))
			outp.extend(raw[self.slen:].tolist())
			self.save = self.save[-self.slen:]
		if fsync_hack:
			return -1 
		else:
		#	self.log('pre trim outp length: %d'%len(outp))
			return outp[:len(sig)-len(pad)+self.slen]
