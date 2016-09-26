from Functions.util import letters2pam,maximumlength
from Parent.Module import Module
from struct import pack
import numpy as np
import pdb
class Prefix(Module):
	def __init__(self, *args, **kwargs):
		Module.__init__(self, *args, **kwargs)
		self.maxbyt = 2**16
		bits = 8 
		for kw in kwargs:
			if kw == 'bits':
				bits = int(kwargs[kw])
		self.prefix = maximumlength(bits) 
		self.log('Prefix Length: %d'%len(self.prefix))
	
	def process(self, byte_data):
		ret = None
		done = False
		while not done:
			packet = None
			if self.maxbyt < len(byte_data):
				pam = letters2pam(pack('H',self.maxbyt-1) + byte_data[:self.maxbyt])
				#self.log('Payload: %s'%str(pam))
				packet = np.append(self.prefix, pam)
				byte_data = byte_data[self.maxbyt:]
			else:
				num_bytes = pack('H', len(byte_data)-1)
				header = letters2pam(num_bytes)
				payload= letters2pam(byte_data)
				#self.log('header : %s'%str(header))
				#self.log('data   : %s'%str(payload))
				pam = np.append(header, payload)
				#self.log('entire : %s'%str(pam))
				packet = np.append(self.prefix, pam)
				done = True
			if ret is None:
				ret = packet
			else:
				ret = np.append(ret, packet)
		self.log('Packet Length %d'%len(ret))
		return ret

			

