from scipy.signal import fftconvolve, firwin, convolve
from numpy.fft import ifft, fft, fftfreq
import matplotlib.pyplot as plt
from numpy.random import random
from time import time
import numpy as np

def plotspec(data, ts = 1, block = False):
	data = data[:-1]
	fft_data = fft(data)/float(len(data))
	fft_axis = 1.0/ts*fftfreq(len(data))
	plt.subplot(311)
	plt.plot(np.arange(0, len(data))*ts, data)
	plt.title('Time Domain')
	plt.ylabel('Amplitude')
	plt.subplot(312)
	plt.plot(fft_axis, 10.0*np.log10(np.abs(fft_data)))

	fft_lim = fft_axis[ np.array([-1,0])+(len(fft_axis)+1)/2]

	plt.xlim(fft_lim)
	plt.title('Magnitude')
	plt.subplot(313)
	plt.plot(fft_axis, np.angle(fft_data)/np.pi)
	plt.xlim(fft_lim)
	plt.ylabel('Phase/pi')
	plt.title('Phase')
	plt.show(block = block)

def ffs(f, fs):
	return fs/np.round(fs/f)

def experiment():
	import matplotlib.pyplot as plt
	
	def conv(sig, fir):
		delta = len(sig) - len(fir)
		if delta > 0:
			delay = len(fir)-1
			fir = fir + [0] * (delay+delta)
			sig = sig + [0] * delay
		elif delta < 0:
			delay = len(sig)-1
			sig = sig + [0] * (delay-delta)
			fir = fir + [0] * delay
		fftsig = fft(sig)
		fftfir = fft(fir)
		fftout = fftsig * fftfir
		out = ifft(fftout).real
		return out

	def peri_convo(sig,fir):
		delta = len(sig) - len(fir)
		if delta > 0:
			fir = fir + [0] * delta
			sig = sig 
		elif delta < 0:
			sig = sig + [0] * -delta
			fir = fir
		fftsig = fft(sig)
		fftfir = fft(fir)
		fftout = fftsig * fftfir
		out = ifft(fftout).real
		return out
		
	def conv_chunk(sig,fir,db=False):
		slen = len(fir)-1 # save len
		size = 128-slen  # size sig chunk + slen = pwr of 2
		pad = [0] * (len(fir) - 1 + size - ((len(fir)+len(sig)-1)%size)) # pad make sig integer number of size
		sig.extend(pad)
		save = [0] * slen 
		outp = []
		for k in range(0, len(sig)/size):
			save.extend(sig[k*size:(k+1)*size])
			if db:
				plt.clf()
				plt.subplot(211)
				plt.plot(save)
				plt.plot(save[0:slen], 'r.')
				plt.title('saved + signal chunk')
			raw = peri_convo(save, fir)
			if db:
				plt.subplot(212)
				plt.plot(raw)
				if len(outp) > len(fir):
					plt.plot(outp[-slen:], 'g')
				plt.title('convolution with (saved + signal chunk) and tri')
				plt.show(block=False)
				plt.pause(.1)
			#print k, k*size, (k+1)*size
			outp.extend(raw[slen:].tolist())
			save = save[-slen:]
		return outp[:len(sig)-len(pad)+len(fir)-1]

	def plot_helper(sig, fir, out, block = False):
		xlim = (0,len(out))

		plt.subplot(311)
		plt.plot(sig)
		plt.xlim(xlim)

		plt.subplot(312)
		plt.plot(fir)
		plt.xlim(xlim)

		plt.subplot(313)
		plt.plot(out)
		plt.xlim(xlim)
		plt.show(block = block)

	def test(num, show=False):
		import pdb
		top = 10 
		tri = range(0, top) + range(top,0,-1)
		sig = tri * (num/len(tri))
		sig+= tri[:num%len(tri)]
		fir = tri
		begi = time()
		out1 = convolve(sig, fir)
		tim1 = time() - begi

#		plt.figure(1)
#		plot_helper(sig, fir, out1)

		out2 = conv(sig, fir)
#		plt.figure(2)
#		plot_helper(sig, fir, out2, False)

#		plt.figure(3)
		begi = time()
		out3 = conv_chunk(sig, fir)
		tim3 = time() - begi
#		plot_helper(sig, fir, out3, True)

		diff = out1-out3 
		return max(diff), tim1, tim3

#	test(100, True)
#	return

	total = 1000
	rands = [int(f) for f in np.round(1.0 + total*1.0*random(total))]
	tim1s = [0]*total
	tim3s = [0]*total

	for k in range(1,total):
		rando = rands[k]
		print '[%5d/%5d]'%(k+1, total) 
		error, tim1, tim3 = test(rando,False)
		if 1E-10 < error:
			print num
			test(num, True)
		tim1s[k] = tim1
		tim3s[k] = tim3
	plt.figure(1)
	plt.plot(rands, tim1s, 'ro')
	plt.plot(rands, tim3s, 'bo')
	plt.show()
if __name__=='__main__':
	experiment()
