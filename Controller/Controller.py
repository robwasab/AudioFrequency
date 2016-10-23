from   Parent.Box import Box
from   unicurses import *
import numpy as np
import pdb

class Module(Box):

	COL_OFFSET = 2
	LINE_TITLE = 1
	LINE_QUEUE_SIZE = 2
	LINE_MESSAGES = 3

	def __init__(self, line, col, height, width, title, queue_size):
		self.data = {}
		self.data['title'] = title
		self.data['queue_size'] = queue_size
		self.data['show'] = False
		self.header = [
		(self.field_format, '%s'            , 'title'),
		(self.field_format, 'Show: %s'      , 'show'),
		(self.field_format, 'Queue size: %d', 'queue_size'),
		(self.bar_format  , 'queue_size'),
		(self.label_format, 'Log:')]

		self.msg_size = 0
		self.max_messages = height-4 if height-4>0 else 0  
		self.messages = ['']*self.max_messages
		self.queue_size = 10
		Box.__init__(self, line, col, height, width)

	def label_format(self, line, offset, *arg):
		mvwaddstr(self.win, line, offset, arg[0])

	def field_format(self, line, offset, *args):
		text = args[0]%self.data[args[1]]
		mvwaddstr(self.win, line, offset, text)
		wclrtoeol(self.win)
		#waddstr(self.win, ' ')

	def bar_format(self, line, offset, *args):
		wattron(self.win, A_REVERSE) 
		bar_room = self.width-2-offset
		queue_size = self.data[args[0]]
		bar = ' '*(queue_size if queue_size<bar_room else bar_room)
		mvwaddstr(self.win, line, offset, bar)
		wattroff(self.win, A_REVERSE)
		wclrtoeol(self.win)
				
	def resize(self, height, width):
		Box.resize(self, height, width)
		new_max = height-len(self.header)-2
		new_messages = ['']*new_max
		self.messages = new_messages
		self.max_messages = new_max
		self.msg_size = 0

	def log(self, msg):
		if self.msg_size < self.max_messages:
			self.messages[self.msg_size] = msg
			self.msg_size += 1
		else:
			self.messages[0:-1] = self.messages[1:]
			self.messages[-1] = msg
		self.draw()
	
	def draw_header(self):
		start = 1
		offset = 2
		for line in self.header:
			line[0](start, offset, *line[1:])
			start += 1

	def draw(self):
		self.draw_header()
		for n in xrange(self.msg_size):
			line = len(self.header)+1+n
			col =  Module.COL_OFFSET
			mvwaddstr(self.win, line, col, self.messages[n])
		Box.draw(self)

CONTROLLER_LISTEN = 0
CONTROLLER_COMMAND = 1

class Controller(Box):
	def __init__(self, modules, line, col):
		LINES, COLS = getmaxyx(stdscr)
		Box.__init__(self,line,col,LINES,COLS)
		self.state = CONTROLLER_LISTEN
		self.command = ''

		self.modules = modules
		self.win = None

		side = self.calc_side()
		for module in self.modules:
			module.resize(side, side)
	
	def add(self, module):
		self.modules.append(module)
	
	def calc_side(self):
		N = len(self.modules)
		area = self.box_height*self.box_width/N
		side = np.sqrt(area)
		xnum = int(np.ceil(self.box_width/side))
		ynum = int(np.ceil(self.box_height/side))
		if xnum > ynum:
			side = self.box_width/xnum
		else:
			side = self.box_height/ynum
		while True:
			xnum = self.box_width/side
			ynum = self.box_height/side
			if xnum*ynum < N:
				side -= 1
			else:
				break
		return side

	def resize(self, height=-1, width=-1):
		if height==-1 and width==-1:
			height,width=getmaxyx(stdscr)

		min_width = min(self.modules, key=lambda x: x.width)
		if width < min_width.box_width:
			raise Exception('width too small')

		side = self.calc_side()
		for module in self.modules:
			module.resize(side, side)

		Box.resize(self, height, width)

	def draw(self):
		start_col  = self.box_col
		start_line = self.box_line
		max_height = -1
		max_col = -1

		side = self.calc_side()
		for module in self.modules:
			module.resize(side, side)

		for n in range(len(self.modules)):
			module = self.modules[n]

			if max_height < module.box_height:
				max_height = module.box_height
			end_col = start_col + module.box_width
			if end_col > max_col:
				max_col = end_col

			if end_col>self.box_col+self.box_width: 
				start_col   = self.box_col
				start_line += max_height 
				max_height = -1
			module.move(start_line, start_col)
			start_col += module.box_width
		for module in self.modules:
			module.draw()

	def reset_terminal(self):
		refresh()
		endwin()

	def work(self):
		c = wgetch(stdscr)
		if self.state == CONTROLLER_LISTEN:
			if c == ord(':'):
				self.state = CONTROLLER_COMMAND	
				self.command = ''
		elif self.state == CONTROLLER_COMMAND:
			if c == ord('\n') or c == 27:
				self.state = CONTROLLER_LISTEN
				if self.command == 'q':
					refresh()
					endwin()
					return False
				elif self.command == 'r':
					LINES, COLS = getmaxyx(stdscr)
					self.resize(LINES, COLS)
					controller.draw()
			else:
				self.command += chr(c)
		return True
