from   Queue import Queue, Full, Empty
from   threading import Thread, Lock
from   threading import Semaphore
from   time import time,sleep
import numpy as np
import traceback
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
	
	
	def reset(self):
		return

	def __init__(self, next_module=None, **kwargs):
		Thread.__init__(self)
		self.output = next_module
		self.mutex  = Lock()
		self.stop   = False	
		self.plt    = None 
		self.fig    = 1
		self.base   = time()
		self.passthrough = False
		self.main   = False
		self.debug  = False
		self.input  = Queue()
		self.input_size_thresh = 1

		for key in kwargs:
			if key == 'fig' :
				self.fig = int(kwargs[key])
			elif key == 'passthrough':
				self.passthrough = bool(kwargs[key])
			elif key == 'plt':
				self.plt = kwargs[key]
			elif key == 'main':
				self.main = bool(kwargs[key])
			elif key == 'debug':
				self.debug = bool(kwargs[key])

	def request_input(self, size):
		self.input_size_thresh = size

	def work(self):
		if not self.input.empty():
			in_data = self.input.get()
			if self.passthrough == True:
				self.output.input.put(in_data)
				return True
			start = time()
			out_dat = self.process(in_data)
			stop  = time()
			#print self.YELLOW + self.__class__.__name__+':\t [%4.3f ms]'%(1000.0*(stop-start))+self.ENDC

			if self.output is not None:
				if out_dat is not None:
					self.output.input.put(out_dat)
			return True
		else:
			return True 
			

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

	def process(self):
		return None
	
	def log(self, msg):
		if type(msg) != str:
			msg = str(msg)
		msg = self.GREEN + self.__class__.__name__ + ':\t'+ self.ENDC + msg
		print msg
	
	def print_kw_error(self, arg_name):
		print Module.FAIL + self.__class__.__name__ + ' requires key word argument %s!'%arg_name + Module.ENDC

	def print_pam(self, pam):
		msg = '\n'
		count = 0
		byte = np.zeros(4)
		for p in pam:
			byte[count%4] = p
			count+=1
			if count%4 == 0:
				msg += '%d: [%2d %2d %2d %2d]\n'%(count/4, byte[0], byte[1], byte[2], byte[3])

		if count%4 > 0:
			msg += '%d: ['%(1+count/4) + ('%2d '*(count%4))%tuple(byte[:count%4]) + '...\n'
		
		self.log(msg)

class MyQueue(object):
	def __init__(self, memory_type, memory_size = 1024):
		self.memory_size = memory_size
		self.memory = np.zeros(self.memory_size, memory_type)
		self.quhead = 0
		self.qutail = 0
		self.qusize = 0
		self.queue_mutex = Lock()

	def resize(self, size):
		self.queue_mutex.acquire()
		self.memory_size = size
		self.memory = np.zeros(self.memory_size)
		self.quhead = 0
		self.qutail = 0
		self.qusize = 0
		self.queue_mutex.release()

	def size(self):
		self.queue_mutex.acquire()
		size = self.qusize
		self.queue_mutex.release()
		return size

	def put(self, data):
		self.queue_mutex.acquire()

		room = len(data) > self.memory_size - self.qusize;

		self.queue_mutex.release()

		if room:
			raise Full("Not enough room in queue")
		
		self.queue_mutex.acquire()

		indexes = (self.qutail + np.arange(len(data)))%self.memory_size
		self.memory[indexes] = data
		self.qusize += len(data)
		
		self.queue_mutex.release()
		
		self.qutail += len(data)

	def read(self, amt):
		if amt > self.size():
			raise Empty("Not enough data to read from")
		
		self.queue_mutex.acquire()

		indexes = (self.quhead + np.arange(amt))%self.memory_size
		self.qusize -= amt
		retreive = self.memory[indexes]
		self.quhead  = (self.quhead + amt)%self.memory_size
		read = self.memory[indexes]

		self.queue_mutex.release()
		return read

	def print_memory(self):
		self.queue_mutex.acquire()
		colsize = int(np.sqrt(len(self.memory)))
		rowsize = len(self.memory_size)/colsize;

		print "col x row = %d"%(colsize*rowsize)

		for y in range(rowsize-1, -1, -1):
			line = '%4d: ['%(y*colsize)
			for x in range(0, colsize):
				line += '\t%5.3f\t'%self.memory[y*colsize + x]
			line += ']\n'
			print line
		self.queue_mutex.release()

