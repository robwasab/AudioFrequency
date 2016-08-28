from Parent.Sink import Sink
import select
import sys
import os

class PlotSink(Sink):
	def __init__(self, *args, **kwargs):
		Sink.__init__(self, *args, **kwargs)
		self.stem = False
		for key in kwargs:
			if key == 'stem':
				self.stem = bool(kwargs[key])

	def process(self, data):
		if self.plt != None:
			os.write(sys.stdout.fileno(), self.YELLOW + self.__class__.__name__+ '[%d]: plotting...'%(self.fig))
			self.plt.figure(self.fig)
			if self.stem:
				self.plt.stem(data)
			else:
				self.plt.plot(data)
			self.plt.show(block = False)
			os.write(sys.stdout.fileno(), self.GREEN + ' Done!' + self.ENDC + '\n')
		else:
			print self.FAIL + self.__class__.__name__+': You must pass plt object as \'plt\' key word argument' + self.ENDC
