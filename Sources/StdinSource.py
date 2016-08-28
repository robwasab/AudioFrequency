from Parent.Source import Source
import select
import sys
import os
import numpy as np
import itertools

def letters2pam(s):
	return list(itertools.chain(*[[int(pair[0] + pair[1],2)*2-3 for pair in np.reshape(list('{:08b}'.format(ord(c))),(4,2))] for c in s]))

class StdinSource(Source):
	def __init__(self, *args, **kwargs):
		Source.__init__(self, *args, **kwargs)
	
	def read(self):
		readable, writeable, execeptional = select.select([sys.stdin.fileno()], [], [], 1.0)
		for fd in readable:
			data = os.read(fd, 1024)
			return letters2pam(data)
