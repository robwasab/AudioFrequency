from   threading import Thread, Semaphore
from   Queue import Queue, Full, Empty
from   time import time,sleep
from   threading import Lock
from   Box import Box
import numpy as np
import traceback
import sys
import pdb
import os

stdout = sys.stdout
output_redirection = False

if len(sys.argv) > 1:
	new_tty = sys.argv[1]
	for root, dirs, files in os.walk('/dev'):
		for f in files:
			if new_tty in f:
				stdout = open(os.path.join(root,f), 'w')
				sys.stderr = stdout
				output_redirection = True
				break
		if output_redirection:
			break

if len(sys.argv) > 1 and not output_redirection:
	print 'Invalid file descriptor'
	sys.exit(-1)

class Module(Thread):
	HEADER = '\033[95m'
	BLUE = '\033[94m'
	CYAN = '\033[36m'
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
		self.zeroed = False

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

		if output_redirection:
			self.box = Box(0,0,0,0)
			self.box_title      = self.box.add_label(self.__class__.__name__)
			self.box_queue_size = self.box.add_label('0')
			self.box_queue_bar  = self.box.add_bar(0)
			self.box_log        = self.box.add_label('log:')
		else:
			self.box = None

	def work(self):
		if not self.input.empty():
			queue_size = len(self.input.queue)
			if self.box is not None:
				self.box.notify(self.box_queue_size, queue_size)
				self.box.notify(self.box_queue_bar, queue_size)
				self.zeroed = False

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
			if self.box is not None and not self.zeroed:
				self.zeroed = True
				self.box.notify(self.box_queue_size, 0)
				self.box.notify(self.box_queue_bar, 0)
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
		self.log(self.__class__.__name__+' starting')
		Module.print_lock.release()
		base = time()
		try:
			while True:
				self.mutex.acquire()
				busy = self.work()
				self.mutex.release()
				if busy:
					base = time()
				else:
					if time() - base > 5.0:
						#sleep(0.5)
						pass

				self.mutex.acquire()
				if self.stop:
					self.mutex.release()
					break
				else:
					self.mutex.release()

		except Exception as e:
			Module.print_lock.acquire()
			self.log(self.FAIL + 'Exception in ' + self.__class__.__name__ + self.ENDC)
			traceback.print_exc()
			Module.print_lock.release()

		Module.print_lock.acquire()
		self.log(self.__class__.__name__+' quitting')
		Module.print_lock.release()

	def process(self):
		return None
	
	def blog(self, msg):
		if self.box is not None:
			self.box.box_log(msg)

	def log(self, msg):
		if type(msg) != str:
			msg = str(msg)
		stdout.write(self.GREEN + self.__class__.__name__ + ':\t'+ self.ENDC + msg + '\n')
	
	def print_kw_error(self, arg_name):
		msg = Module.FAIL + self.__class__.__name__ + ' requires key word argument %s!'%arg_name + Module.ENDC
		self.log(msg)
		self.box_log(msg)

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

