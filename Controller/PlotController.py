from   Scope import Scope
from   Queue import Queue
import numpy as np


class PlotController(object):
	mpl_inited = False

	def __init__(self):
		self.modules = []
	
	def add_module(self, module, buffer_size=2**11):
		if module not in self.modules:
			s = Scope(buffer_size)
			s.set_title(module.__class__.__name__)
			module.set_scope(s)
			self.modules.append(module)
			self.partition()
			return True
		return False
	
	def rm_module(self, module):
		try:
			n = self.modules.index(module)
			self.modules[n].set_scope(None)
			del self.modules[n]
			if len(self.modules) == 0:
				self.plt.close(0)
			else:
				self.partition()
			return True
		except ValueError:
			return False

	def partition(self):
		if not PlotController.mpl_inited:
			import matplotlib.pyplot as plt
			self.plt = plt
			PlotController.mpl_inited = True	
		
		self.plt.figure(0, facecolor='white')
		self.plt.gcf().clf()
		rows = 2 
	
		if len(self.modules) == 1:
			rows = 1

		N = np.ceil(len(self.modules)/float(rows))
		size = N*rows
		cols = int(size/rows)
		rows = int(rows)
		geom = (rows, cols)
		loc  = [0, 0]
		for m in self.modules:
			ax1 = self.plt.subplot2grid(geom, loc)
			m.scope.set_ax(ax1)
			ax1.set_title(m.__class__.__name__)
			loc[1] += 1
			if loc[1] >= cols:
				loc[1] = 0
				loc[0] += 1

		self.plt.show(block=False)
		self.plt.gcf().canvas.draw()
	
	def work(self):
		for m in self.modules:
			m.scope.work()
