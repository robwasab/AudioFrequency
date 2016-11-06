from   matplotlib import gridspec 
import matplotlib.pyplot as plt
from   threading import Lock
from   Queue import Queue
import numpy as np
import pdb

class Scope(object):
	def __init__(self, size, ax, fmt='.'):
		self.buffer   = np.zeros(size)
		self.queue    = Queue()
		self.ax       = ax
		self.overflow = []
		self.size     = 0
		self.handle   = None
		self.fmt = fmt 
	
	def work(self):
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

	def set_ax(self, ax):
		self.ax = ax
		self.handle = None

def partition(modules):
	plt.gcf().clf()
	rows = 2 

	if len(modules) == 1:
		rows = 1

	N = np.ceil(len(modules)/float(rows))
	size = N*rows
	cols = int(size/rows)
	rows = int(rows)
	geom = (rows, cols)
	loc  = [0, 0]
	for m in modules:
		ax1 = plt.subplot2grid(geom, loc)
		m.set_ax(ax1)
		loc[1] += 1
		if loc[1] >= cols:
			loc[1] = 0
			loc[0] += 1
	plt.show(block=False)
	plt.gcf().canvas.draw()

plt.figure(facecolor='white')	
plt.show(block=False)
s1 = Scope(1024, plt.gca()) 
N = 2**13
times = np.arange(N)/float(N)
signal = np.cos(2.0*np.pi*100.0*times)*np.cos(2.0*np.pi*10.0*times)

s1.queue.put(signal)
while True:
	s1.work()
	if 'q' == raw_input():
		break


scopes = []
N = 1024

for n in range(5):
	s = Scope(N, None)
	N += N/2
	s.queue.put(signal)
	scopes.append(s)

partition(scopes)

while True:
	for s in scopes:
		s.work()
	if 'q' == raw_input():
		break
scopes = []
N = 1024

for n in range(3):
	s = Scope(N, None)
	N += N/2
	s.queue.put(signal)
	scopes.append(s)

partition(scopes)

while True:
	for s in scopes:
		s.work()
	if 'q' == raw_input():
		break

scopes = []
N = 1024

for n in range(2):
	s = Scope(N, None)
	s.queue.put(signal)
	scopes.append(s)

partition(scopes)

while True:
	for s in scopes:
		s.work()
	if 'q' == raw_input():
		break

partition(scopes[:1])
scopes[0].queue.put(signal)

while True:
	for s in scopes:
		s.work()
	if 'q' == raw_input():
		break

