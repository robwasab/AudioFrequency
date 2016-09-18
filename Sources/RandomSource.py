from   Parent.Source  import Source
from   Functions.util import quantize
import select
import sys
import os
import numpy as np
import pdb

class RandomSource(Source):
	def __init__(self, *args, **kwargs):
		Source.__init__(self, *args, **kwargs)
		self.num = 5000 
		self.data = ''

	def read(self):
		readable, writeable, execeptional = select.select([sys.stdin.fileno()], [], [], 1.0)
		for fd in readable:
			os.read(fd, 1024)
			print self.YELLOW + 'Creating random data..' + self.ENDC
			self.data = ''.join([chr(int(r)+ord('a')) for r in np.round(25*np.random.rand(self.num))])
			self.log('\n>> '+self.data)
			return self.data
