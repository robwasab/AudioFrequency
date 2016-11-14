from   Parent.Module import Module
import numpy as np

class Noise(Module):

	def __init__(self, *args, **kwargs):
		Module.__init__(self, *args, **kwargs)
		self.snr = 1E9
		for key in kwargs:
			if key == 'snr':
				self.snr = kwargs[key]
			elif key == 'snr_db':
				self.snr = np.power(10, kwargs[key]/10.0)
		if self.box is not None:
			self.box_snr_label = self.box.add_label('snr [dB]: %.3f'%self.snr2db())
		
	def snr2db(self):
		return 10.0*np.log10(self.snr)

	def calc_pwr(self, signal):
		return np.sum(np.power(signal,2))/float(len(signal))

	def set_snr(self, new_snr):
		self.mutex.acquire()
		self.snr = new_snr
		self.mutex.release()
		if self.box is not None:
			self.box.notify(self.box_snr_label, 'snr [dB]: %.3f'%self.snr2db())

	def process(self, signal):
		noise_pwr = self.calc_pwr(signal)/self.snr
		return signal + np.sqrt(noise_pwr)*np.random.randn(len(signal))

	def cmd_info(self):
		new_cmd_info = [('snr_db', 'set snr ratio'),
				('snr'   , 'set snr ratio')]
		old_cmd_info = Module.cmd_info(self)
		old_cmd_info.extend(new_cmd_info)
		return old_cmd_info
		
		
	def interpret_cmd(self, cmd):
		cmd_arg = cmd.split(' ')
		if len(cmd_arg) < 2:
			return
		cmd = cmd_arg[0]
		arg = float(cmd_arg[1])
		if cmd == 'snr_db':
			self.set_snr(np.power(10.0, arg/10.0))
		elif cmd == 'snr':
			self.set_snr(arg)
