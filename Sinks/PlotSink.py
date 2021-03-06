from Parent.Sink import Sink
import numpy as np
import select
import sys
import os

class PlotSink(Sink):
	def __init__(self, *args, **kwargs):
		Sink.__init__(self, *args, **kwargs)
		self.stem = False
		self.persist = False
		for key in kwargs:
			if key == 'stem':
				self.stem = bool(kwargs[key])
			elif key == 'persist':
				self.persist = bool(kwargs[key])
		self.data = []
		
	def process(self, data):
		if self.plt != None:
			self.data = np.append(self.data, data)
			#os.write(sys.stdout.fileno(), self.YELLOW + self.__class__.__name__+ '[%d]: plotting...'%(self.fig))
			self.plt.figure(self.fig)
			if not self.persist:
				self.plt.clf()
			if self.stem:
				self.plt.stem(self.data)
			else:
				self.plt.plot(self.data)
			self.plt.show(block = self.debug)
			self.plt.pause(0.01)
			#os.write(sys.stdout.fileno(), self.GREEN + ' Done!' + self.ENDC + '\n')
		else:
			print self.FAIL + self.__class__.__name__+': You must pass plt object as \'plt\' key word argument' + self.ENDC
		return data
