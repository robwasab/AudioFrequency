from   Parent.Box import Box
from   unicurses import *
import numpy as np
import pdb
import os

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

		min_width = min(self.modules, key=lambda x: x.box_width)
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

		if self.state == CONTROLLER_COMMAND:
			if c == ord('\n') or c == 27:
				self.command = self.command[1:]
				self.state = CONTROLLER_LISTEN
				move(0, 0)
				clrtoeol()

				if self.command == 'q':
					refresh()
					endwin()
					return False
				elif self.command == 'r':
					LINES, COLS = getmaxyx(stdscr)
					self.resize(LINES, COLS)
					self.draw()

				else:
					self.modules[0].input.put(self.command)
			else:
				if c == 127:
					if len(self.command) == 1:
						self.state = CONTROLLER_LISTEN
						move(0,0)
						clrtoeol()
					self.command = self.command[:-1]
				else:
					self.command += chr(c)
				attron(A_REVERSE) 
				mvaddstr(0, 0, '%s\n'%self.command)
				attroff(A_REVERSE) 
				clrtoeol()
		return True
