from Module import Module

class Sink(Module):
	def __init__(self, output = None, **kwargs):
		Module.__init__(self, output, **kwargs)

	def process(self, in_data):
		return None
