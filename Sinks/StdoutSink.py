from Parent.Sink import Sink
import select
import sys
import os

class StdoutSink(Sink):
	def __init__(self, *args, **kwargs):
		Sink.__init__(self, *args, **kwargs)
		self.data = ''
		self.done = False
			
	def process(self, data):
		readable, writeable, exceptional = select.select([], [sys.stdout.fileno()], [])
		for fd in writeable:
			header = self.GREEN + 'TYPE: ' + str(type(data))
			try:
				header += ' LENGTH: %d' % (len(data))
			except Exception:
				pass
			header += self.ENDC + '\n>> '
			#os.write(fd,  header + str(data) + '\n')
			self.log('[Receiving data!]\n'+header+str(data))
			self.data = data
			self.done = True
		return data
