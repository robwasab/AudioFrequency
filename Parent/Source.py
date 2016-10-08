from Module import Module

class Source(Module):
	def __init__(self, *args, **kwargs):
		Module.__init__(self, *args, **kwargs)

	def work(self):
		data = self.read()
		if data is not None:
			self.output.input.put(data)
			return True
		return False

	def read(self):
		return None 
