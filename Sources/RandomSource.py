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

	def read(self):
		readable, writeable, execeptional = select.select([sys.stdin.fileno()], [], [], 1.0)
		for fd in readable:
			os.read(fd, 1024)
			print self.YELLOW + 'Creating random data..' + self.ENDC
			data = [quantize(r) for r in 6.0*np.random.rand(self.num)-3.0] 
			return data
