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
		self.set_bcoef(self.bcoef)
		self.flush = False 
		for kw in kwargs:
			if kw == 'flush':
				self.flush = kwargs[kw]
	
	def set_bcoef(self, bcoef):
		self.bcoef = bcoef
		self.slen  = len(self.bcoef) - 1
		self.save  = np.zeros(self.slen)
		self.chunklen = 2 
		efficiency = (self.chunklen - self.slen)/float(self.chunklen)

		while efficiency < 0.75:
			self.chunklen *= 2
			efficiency = (self.chunklen - self.slen)/float(self.chunklen)
		self.log('Efficiency: %%%3.3f\tChunk Len: %5d\tSave Len: %4d'%(100.0*efficiency, self.chunklen, self.slen))
		self.periodic_mode = False

	def process(self, signal):
		return self.conv_chunk_chunk(signal, False, self.flush)
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

	def conv_chunk_chunk(self, data, fsync_hack=False, flush=False):
		signal = np.append(self.save, data)
		if flush:
			signal = np.append(signal, np.zeros(self.slen))

		filtered = peri_convo(signal, self.bcoef)[self.slen:]

		self.save= signal[-self.slen:]

		if fsync_hack:
			filtered_abs = np.abs(filtered)
			idx = np.argmax(filtered_abs)
			if filtered_abs[idx] > 0.5: 
				s = np.sign(filtered[idx])
				return idx
			return -1 
		return filtered

	def conv_chunk(self,data,fsync_hack=False, debug=False):
		size = self.chunklen - self.slen  # size sig chunk + slen = pwr of 2
		pad  = np.zeros(self.chunklen - ((self.slen+len(data))%size)) # pad make sig integer number of size
		sig  = np.append(data, pad)
		outp = np.zeros(len(data) + len(pad) + self.slen)
		ncyc = len(sig)/size
		if debug:
			self.log(' len(data) : %d' % len(data))
			self.log(' chunk len : %d' % self.chunklen)
			self.log(' save  len : %d' % self.slen)
			self.log(' read size : %d' % size)
			self.log(' pading    : %d' % len(pad))
			self.log(' len(data)+padding: %d'%len(sig))
			self.log('(len(data)+padding)%%read size: %d'%(len(sig)%size))
			self.log(' ncycles   : %d'%ncyc)
			self.plt.figure(self.fig)
			self.plt.gcf().clf()
			self.plt.subplot(211)
			self.plt.plot(self.bcoef)
			self.plt.ylim((-2,2))
			self.plt.title('Reference')
			self.plt.subplot(212)
			self.plt.plot(data)
			self.plt.title('Data')
			self.plt.show(block=True)
			self.save_handle = None
			self.raw_handle = None
	
		for k in range(0, ncyc):
		#	if not fsync_hack:
		#		self.log('[%d/%d]:'%(k,ncyc))
		#		self.log('        type(self.save ): ' + str(type(self.save)))
		#		self.log('        type(self.bcoef): ' + str(type(self.bcoef)))
		#		self.log('        save  length %d'%len(self.save))
		#		self.log('        bcoef length %d'%len(self.bcoef))
			self.save = np.append(self.save, sig[k*size:(k+1)*size])
			raw = peri_convo(self.save, self.bcoef)[self.slen:]

			if debug:
				if self.save_handle == None:
					self.plt.figure(self.fig)
					self.plt.subplot(211)
					self.save_handle, = self.plt.plot(self.save)
					self.plt.title('save')
					self.plt.ylim((-20,20))
				else:
					self.save_handle.set_ydata(self.save)

				if self.raw_handle == None:
					self.plt.figure(self.fig)
					self.plt.subplot(212)
					self.raw_handle, = self.plt.plot(raw)
					self.plt.title('raw')
					self.plt.ylim((-3, 3))
					self.plt.show(block = False)
				else:
					self.raw_handle.set_ydata(raw)
	
				self.plt.gcf().canvas.draw()
				self.plt.pause(0.5)
				raw_input('press enter to continue')

			if fsync_hack:
				raw_abs = np.abs(raw)
				idx = np.argmax(raw_abs)
				if raw_abs[idx] > 0.5: 
					start_idx = k*size + idx
					if debug:
						self.log('k       : %d'%k)
						self.log('len(raw): %d'%len(raw))
						self.log('idx     : %d'%idx)
						self.log('slen    : %d'%self.slen)
						self.log('k*size+size+idx = %d'%start_idx)
					s = np.sign(raw[idx])
					return (start_idx, s)
			#else:
			#	self.log('[%d/%d] raw len: %d slen: %d'%(k,len(sig)/size, len(raw), self.slen))
			outp[k*size:(k+1)*size] = raw
			self.save = self.save[-self.slen:]
		if fsync_hack:
			self.log('return -1')
			return -1, 0 
		else:
		#	self.log('pre trim outp length: %d'%len(outp))
			if self.periodic_mode:
				return outp[:len(sig)-len(pad)]
			else:
				return outp[:len(sig)-len(pad)+self.slen]
