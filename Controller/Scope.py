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
		self.plot_properties = {}
		self.plot_properties['ylim']  = [Queue(), (-1,1), True, lambda self: self.ax.set_ylim (self.plot_properties['ylim'][1])]
		self.plot_properties['title'] = [Queue(), ''    , True, lambda self: self.ax.set_title(self.plot_properties['title'][1])]

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

		if self.size >= len(self.buffer):
			if self.handle is None:
				self.handle, = self.ax.plot(np.arange(len(self.buffer)), self.buffer, self.fmt)
				self.ax.set_xlim((0,len(self.buffer)))
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

	def set_property(self, key, value):
		self.plot_properties[key][0].put(value)
	
	def set_title(self, title):
		self.set_property('title', title)

	def set_ylim(self, top, bot=None):
		if bot is None:
			self.set_property('ylim', (-top, top))
		else:
			self.set_property('ylim', ( bot, top))

	def set_ax(self, ax):
		self.ax = ax
		self.handle = None
