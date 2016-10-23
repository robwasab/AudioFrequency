from   unicurses import *
import numpy as np
import pdb

class Box(object):
	def __init__(self, line, col, height, width):
		self.line = line
		self.col = col
		self.width = width
		self.height = height
		self.win = newwin(self.height, self.width, self.line, self.col)
		self.draw()
	
	def erase(self):
		werase(self.win)
		wrefresh(self.win)
	
	def draw(self):
		box(self.win, 0, 0)
		wrefresh(self.win)

	def resize(self, height, width):
		self.erase()
		delwin(self.win)
		self.width = width
		self.height = height
		self.win = newwin(self.height, self.width, self.line, self.col)
	
	def move(self, line, col):
		self.erase()
		delwin(self.win)
		self.line = line
		self.col = col
		self.win = newwin(self.height, self.width, self.line, self.col)

class Controller(Box):
	def __init__(self, line, col, height, width, modules):
		self.modules = modules
		self.win = None
		self.height = height
		self.width = width
		side = self.calc_side()
		for module in self.modules:
			module.resize(side, side)
		Box.__init__(self, line, col, height, width)
	
	def add(self, module):
		self.modules.append(module)
	
	def calc_side(self):
		N = len(self.modules)
		area = self.height*self.width/N
		side = np.sqrt(area)
		xnum = int(np.ceil(self.width/side))
		ynum = int(np.ceil(self.height/side))
		if xnum > ynum:
			side = self.width/xnum
		else:
			side = self.height/ynum
		while True:
			xnum = self.width/side
			ynum = self.height/side
			if xnum*ynum < N:
				side -= 1
			else:
				break
		return side

	def resize(self, height, width):
		min_width = min(self.modules, key=lambda x: x.width)
		if width < min_width.width:
			raise Exception('width too small')

		side = self.calc_side()
		for module in self.modules:
			module.resize(side, side)

		Box.resize(self, height, width)

	def draw(self):
		start_col = self.col
		start_line = self.line
		max_height = -1
		max_col = -1

		side = self.calc_side()
		for module in self.modules:
			module.resize(side, side)

		for n in range(len(self.modules)):
			module = self.modules[n]

			if max_height < module.height:
				max_height = module.height
			end_col = start_col + module.width
			if end_col > max_col:
				max_col = end_col

			if end_col > self.col+self.width: 
				start_col = self.col
				start_line += max_height 
				max_height = -1
			module.move(start_line, start_col)
			start_col += module.width
		for module in self.modules:
			module.draw()

stdscr = initscr()
clear()
noecho()
cbreak()
curs_set(0)
refresh()
LINES, COLS = getmaxyx(stdscr)
boxes = [Module(0,0,0,0, 'Test 0', 10)]
controller = Controller(0, 0, LINES, COLS, boxes)
count = 1
while True:
	c = wgetch(stdscr)
	if c == ord('q'):
		break
	elif c == ord('a'):
		boxes.append(Module(0,0,0,0, 'Test %d'%count, 10))
		count += 1
		controller.draw()
	elif c == ord('m'):
		for b in boxes:
			b.log('hello world')
	elif c == ord('n'):
		for b in boxes:
			b.log('world hello')
	elif c == ord('s'):
		for b in boxes:
			b.data['show'] ^= True
			b.draw()
	elif c == ord('u'):
		for b in boxes:
			b.data['queue_size'] += 1
			b.draw()
	elif c == ord('U'):
		for b in boxes:
			b.data['queue_size'] -= 1
			b.draw()
	elif c == ord('r'):
		LINES, COLS = getmaxyx(stdscr)
		controller.resize(LINES, COLS)
		controller.draw()
refresh()
endwin()
