from Functions.util import letters2pam,maximumlength
from Parent.Module import Module
from struct import pack
import numpy as np
import pdb
class Prefix(Module):
	def __init__(self, *args, **kwargs):
		Module.__init__(self, *args, **kwargs)
		self.prsize = 2**8
		self.maxbyt = 2**16
		self.prefix = maximumlength(8) 
	
	def process(self, byte_data):
		ret = None
		done = False
		while not done:
			packet = None
			if self.maxbyt < len(byte_data):
				packet = np.append(self.prefix,letters2pam(pack('H',self.maxbyt-1) + byte_data[:self.maxbyt]))
				byte_data = byte_data[self.maxbyt:]
			else:
				packet = np.append(self.prefix,letters2pam(pack('H',len(byte_data))+ byte_data))
				done = True
			if ret is None:
				ret = packet
			else:
				ret = np.append(ret, packet)
		return ret

			

