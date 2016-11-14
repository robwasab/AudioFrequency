from   scipy import signal
from   Queue import Queue
import numpy as np

# window types: for reference
# boxcar
# triang
# blackman
# hamming
# hann
# bartlett
# flattop
# parzen
# bohman
# blackmanharris
# nuttall
# barthann
# kaiser (needs beta)
# gaussian (needs sigma)
# https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.signal.get_window.html#scipy.signal.get_window

class Scope(object):
	def __init__(self, size=1024, ax=None, fmt='.'):
		self.buffer   = np.zeros(size)
		self.queue    = Queue()
		self.ax       = ax
		self.overflow = []
		self.size     = 0
		self.handle   = None
		self.fmt = fmt 
		self.fft = False
		self.fft_win_type = 'boxcar'
		self.fft_win = signal.get_window(self.fft_win_type, size)
		self.fft_fs = 44.1E3
		self.title = ''
		self.ytop = 1
		self.ybot = -1
		self.plot_properties = {}
		self.plot_properties['ylim' ] = [Queue(), (-1,1), True, lambda self: self.ax.set_ylim (self.plot_properties['ylim' ][1])]
		self.plot_properties['title'] = [Queue(), ''    , True, lambda self: self.__set_title (self.plot_properties['title'][1])]
		self.plot_properties['size' ] = [Queue(), size  , False,lambda self: self.__set_size  (self.plot_properties['size' ][1])]
		self.plot_properties['fft'  ] = [Queue(), size  , False,lambda self: self.__set_fft   (self.plot_properties['fft'  ][1])]
		self.plot_properties['fft_fs']= [Queue(), 44.1E3, False,lambda self: self.__set_fft_fs(self.plot_properties['fft_fs'][1])]

	def work(self):
		if self.ax is None:
			return
		# Data plotting using queues
		data = None
		if len(self.overflow) > 0 and self.size < len(self.buffer):
			data = self.overflow.pop()

		elif not self.queue.empty() and self.size < len(self.buffer):
			data = self.queue.get()

		if data is not None:
			room = len(self.buffer) - self.size
			if len(data) > room:
				self.buffer[self.size:] = data[:room]
				self.overflow.append(data[room:])
				self.size = len(self.buffer)
			else:
				self.buffer[self.size:self.size+len(data)] = data[:]
				self.size += len(data)

		# TODO figure out how to flush this
		if self.size >= len(self.buffer):
			if self.handle is None:
				if self.fft:
					spectra = 20.0*np.log10(np.abs(np.fft.rfft(self.buffer))/float(len(self.buffer)))
					Fs = np.arange(len(self.buffer)/2+1)/float(len(self.buffer))*self.fft_fs
					self.handle, = self.ax.plot(Fs, spectra)
					self.ax.set_xlim((0, Fs[-1]))
					self.ax.set_ylim((-100, 3.0))
				else:
					self.handle, = self.ax.plot(np.arange(len(self.buffer)), self.buffer, self.fmt)
					self.ax.set_xlim((0,len(self.buffer)))
				self.ax.set_title(self.title)
			else:
				if self.fft:
					spectra = 20.0*np.log10(np.abs(np.fft.rfft(self.buffer))/float(len(self.buffer)))
					self.handle.set_ydata(spectra)
				else:
					self.handle.set_ydata(self.buffer)
			self.size = 0
			self.ax.figure.canvas.draw()

		# update plot properties
		for key in self.plot_properties:
			prop = self.plot_properties[key]
			if not prop[0].empty():
				new_value = prop[0].get()
				prop[1] = new_value
				prop[2] = True

			if prop[2]:
				prop[2] = False
				prop[3](self)

	def put(self, data):
		self.queue.put(np.array(data, dtype=np.float32))

	def __set_size(self, new_size):
		if len(self.buffer) != new_size:
			new_buffer = np.zeros(new_size)
			end = self.size if self.size < new_size else new_size
			new_buffer[:end] = self.buffer[:end]
			self.buffer = new_buffer
			self.handle = None
			self.fft_win = signal.get_window(self.fft_win_type, new_size)
			self.ax.cla()
	
	def __set_fft(self, enable_fft):
		if enable_fft != self.fft:
			self.fft = enable_fft
			self.handle = None
			self.ax.cla()
	
	def __set_fft_fs(self, new_fs):
		if new_fs != self.fft_fs:
			self.fft_fs = new_fs
			handle = None
			self.ax.cla()
	
	def __set_title(self, new_title):
		if self.title != new_title:
			self.title = new_title
			self.ax.set_title(new_title)

	def __set_property(self, key, value):
		self.plot_properties[key][0].put(value)
	
	def set_fft(self, enable_fft):
		self.__set_property('fft', enable_fft)
	
	def set_fft_fs(self, new_fs):
		self.__set_property('fft_fs', new_fs)
	
	def set_size(self, new_size):
		self.__set_property('size', new_size)

	def set_title(self, title):
		self.__set_property('title', title)

	def set_ylim(self, top, bot=None):
		if bot is None:
			self.__set_property('ylim', (-top, top))
			self.ytop = top
			self.ybot = -top
		else:
			self.__set_property('ylim', ( bot, top))
			self.ytop = top
			self.ytop = -top

	def set_ax(self, ax):
		self.ax = ax
		self.handle = None

