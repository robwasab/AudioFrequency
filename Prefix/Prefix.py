from   Functions.util    import maximumlength
from   Whitener.Whitener import Whitener
from   Parent.Module     import Module
from   struct            import pack
import itertools
import numpy as np
import pdb

class Prefix(Module):
	def __init__(self, *args, **kwargs):
		Module.__init__(self, *args, **kwargs)
		self.maxbyt = 2**16
		bits = 10 
		for kw in kwargs:
			if kw == 'bits':
				bits = int(kwargs[kw])
		self.prefix = maximumlength(bits) 
		#self.cipher = self.make_cipher()
		#self.prepam = self.num2pam(self.cipher)
		#self.log(self.prepam)	
		#self.log(self.prefix)
		#self.prepam = self.prefix
		if self.debug and self.plt is not None:
			self.plt.figure(self.fig)
			self.plt.gcf().clf()
			self.plt.stem(self.prepam)
			self.plt.title('Initialization: Prefix PAM Header')
			self.plt.show(block=False)
		# formats the maximum length sequence as little endian
		#self.whiten = Whitener(cipher = self.cipher, disable = True)

	def make_cipher(self):
		prefix = np.append(self.prefix, self.prefix[0])
		return [np.sum([bit<<n for n,bit in enumerate([int(b) for b in (1.0+byte)/2.0])]) for byte in np.reshape(prefix, (len(prefix)/8, 8))]

	def text2num(self, text):
		return [ord(c) for c in text]

	def num2text(self, numbers):
		return ''.join([chr(n) for n in numbers])

	def num2pam(self, numbers):
		return list(itertools.chain(*[[int(pair[0] + pair[1],2)*2-3 for pair in np.reshape(list('{:08b}'.format(b)),(4,2))] for b in numbers]))

	def process(self, byte_data):
		self.log(byte_data)
		ret = None
		done = False
		#self.whiten.reset()
		while not done:
			packet = None
			if self.maxbyt < len(byte_data):
				text   = pack('H',self.maxbyt-1) + byte_data[:self.maxbyt]
				numb   = self.text2num(text)
				#scram  = self.whiten.process(numb)
				#pam    = self.num2pam(scram) 
				pam    = self.num2pam(numb)
				#packet = np.append(self.prepam, pam)
				packet = np.append(self.prefix, pam)
				byte_data = byte_data[self.maxbyt:]
			else:
				text   = pack('H', len(byte_data)-1) + byte_data
				numb   = self.text2num(text)
				self.log('payload with length: ' + str(numb))
				#scram  = self.whiten.process(numb)
				#self.log('payload post whiten: ' + str(scram))
				#pam    = self.num2pam(scram)
				pam = self.num2pam(numb)
				self.print_pam(pam)

				#packet = np.append(self.prepam, pam)
				packet = np.append(self.prefix, pam)
				done   = True

			if ret is None:
				ret = packet
			else:
				ret = np.append(ret, packet)
		self.log('Packet Length %d'%len(ret))
		return ret

