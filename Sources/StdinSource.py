from Functions.util import letters2pam
from Parent.Source  import Source
import numpy as np
import select
import sys
import os


class StdinSource(Source):
	def __init__(self, *args, **kwargs):
		Source.__init__(self, *args, **kwargs)
	
	def read(self):
		readable, writeable, execeptional = select.select([sys.stdin.fileno()], [], [], 1.0)
		for fd in readable:
			data = os.read(fd, 1024)
			self.log('[Beginning transmission!]\n>> '+data)
			return data
