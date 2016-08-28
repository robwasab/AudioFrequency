import numpy as np
from   numpy.fft import fft, fftfreq
from   Parent.Sink import Sink

class Plotspec(Sink):
	def __init__(self, *args, **kwargs):
		Sink.__init__(self, *args, **kwargs)
		self.ts = 1
		for key in kwargs:
			if key == 'ts':
				self.ts = float(kwargs[key])
			elif key == 'fs':
				self.ts = 1.0/float(kwargs[key])
			
	def process(self, data):
		if self.plt != None:
			data = data[:-1]
			fft_data = fft(data)/float(len(data))
			fft_axis = fftfreq(len(data))
			self.plt.figure(self.fig)
		
			self.plt.subplot(311)
			self.plt.cla()
			self.plt.plot(np.arange(0, len(data))*self.ts, data)
			self.plt.title('Time Domain')
			self.plt.ylabel('Amplitude')

			self.plt.subplot(312)
			self.plt.cla()
			self.plt.plot(fft_axis, np.abs(fft_data))
			fft_lim = fft_axis[ np.array([-1,0])+(len(fft_axis)+1)/2]
			self.plt.xlim(fft_lim)
			self.plt.title('Magnitude')
		
			self.plt.subplot(313)
			self.plt.cla()
			self.plt.plot(fft_axis, np.angle(fft_data)/np.pi)
			self.plt.xlim(fft_lim)
			self.plt.ylabel('Phase/pi')
			self.plt.title('Phase')
			self.plt.pause(.1)
		else:
			print self.YELLOW + 'No plt object. Pass as key word argument \'plt\'' + self.ENDC
