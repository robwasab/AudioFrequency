from   Utility.PlotClient import PlotClient
from   threading import Thread, Lock 
from   time import time,sleep
import traceback
import Queue
import sys
import pdb

class Module(Thread):
	HEADER = '\033[95m'
	BLUE = '\033[94m'
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'
	print_lock = Lock()
	
	def __init__(self, next_module = None, **kwargs):
		Thread.__init__(self)
		self.input  = Queue.Queue()
		self.output = next_module
		self.mutex  = Lock()
		self.stop   = False	
		self.plt    = None 
		self.fig    = 1
		self.base   = time()
		self.passthrough = False
		self.main   = False
		self.debug  = False
		for key in kwargs:
			if   key == 'port':
				self.server_port = int(kwargs[key])
			elif key == 'fig' :
				self.fig = int(kwargs[key])
			elif key == 'passthrough':
				self.passthrough = bool(kwargs[key])
			elif key == 'plt':
				self.plt = kwargs[key]
			elif key == 'main':
				self.main = bool(kwargs[key])
			elif key == 'debug':
				self.debug = bool(kwargs[key])
	def work(self):
		if not self.input.empty():
			in_data = self.input.get()
			if self.passthrough == True:
				self.output.input.put(in_data)
				return True
			start = time()
			out_dat = self.process(in_data)
			stop  = time()
			print self.YELLOW + self.__class__.__name__+':\t [%4.3f ms]'%(1000.0*(stop-start))+self.ENDC

			if self.output is not None:
				if out_dat is not None:
					self.output.input.put(out_dat)
				else:
					self.output.input.put(in_data)
			return True
		else:
			return False
			

	def quit(self, all = False):
		self.mutex.acquire()
		self.stop = True 
		self.mutex.release()
		if all and self.output != None:
			self.output.quit(True)
		if not self.main:
			self.join()	

	def start(self):
		if not self.main:
			Thread.start(self)
		if self.output != None:
			self.output.start()
		
	def run(self):
		Module.print_lock.acquire()
		print self.__class__.__name__,' starting'
		Module.print_lock.release()
		base = time()
		try:
			while True:
				busy = self.work()
				if busy:
					base = time()
				else:
					if time() - base > 5.0:
						sleep(0.5)

				self.mutex.acquire()
				if self.stop:
					self.mutex.release()
					break
				else:
					self.mutex.release()

		except Exception as e:
			Module.print_lock.acquire()
			print self.FAIL + 'Exception in ' + self.__class__.__name__ + self.ENDC
			traceback.print_exc()
			Module.print_lock.release()

		Module.print_lock.acquire()
		print self.__class__.__name__,' quitting'
		Module.print_lock.release()

	def process(self, input_data):
		return input_data
	
	def log(self, msg):
		if type(msg) != str:
			msg = str(msg)
		msg = self.GREEN + self.__class__.__name__ + ': '+ self.ENDC + msg
		print msg
