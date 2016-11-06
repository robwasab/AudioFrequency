from   Queue import Queue
import numpy as np

class Scope(object):
	def __init__(self, size=1024, ax=None, fmt='.'):
		self.buffer   = np.zeros(size)
		self.queue    = Queue()
		self.ax       = ax
		self.overflow = []
		self.size     = 0
		self.handle   = None
		self.fmt = fmt 
		self.title = ''

	def work(self):
		if self.ax is None:
			return
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

		if self.size >= len(self.buffer):
			if self.handle is None:
				self.handle, = self.ax.plot(np.arange(len(self.buffer)), self.buffer, self.fmt)
				self.ax.set_xlim((0,len(self.buffer)))
				self.ax.title(self.title)
			else:
				self.handle.set_ydata(self.buffer)
			self.size = 0
			self.ax.figure.canvas.draw()

	def set_title(self, title):
		self.title = title

	def set_ax(self, ax):
		self.ax = ax
		self.handle = None
