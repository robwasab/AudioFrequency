from   Parent.Box import Box
from   Queue import Queue
from   unicurses import *
import numpy as np
import select
import sys
import pdb
import os

CNTRL_LISTEN = 0
CNTRL_CMD    = 1
CNTRL_EXEC   = 2
MY_KEY_ESC   = 27
MY_KEY_DEL   = 127

class Controller(Box):
	def __init__(self, modules, line, col):
		self.enable = False
		LINES = 0
		COLS = 0
		self.state = CNTRL_LISTEN
		self.command = ''
		self.modules = []
		for module in modules:
			self.modules.append(module)

		if len(sys.argv) > 1:
			LINES, COLS = getmaxyx(Box.stdscr)
			self.enable = True

			r,w = os.pipe()
			self.source_fd = w
			(self.get_source()).stdin_fd = r
		

		Box.__init__(self,line,col,LINES,COLS)
		side = self.calc_side()
	
	def get_source(self):
		for module in self.modules:
			if module.__class__.__name__ == 'StdinSource':
				return module

	def get_boxes(self):
		boxes = []
		for m in self.modules:
			if m.box is not None:
				boxes.append(m.box)
		return boxes

	def calc_side(self):
		boxes = self.get_boxes()
		N = len(boxes)
		if N < 1:
			return False
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
		for b in boxes:
			b.resize(side, side)
		return True

	def resize(self, height=-1, width=-1):
		if height==-1 and width==-1:
			height,width=getmaxyx(Box.stdscr)

		min_width = min(self.get_boxes(), key=lambda x: x.box_width)
		if width < min_width.box_width:
			raise Exception('width too small')

		self.calc_side()
		Box.resize(self, height, width)

	def draw(self):
		start_col  = self.box_col
		start_line = self.box_line
		max_height = -1
		max_col = -1

		if not self.calc_side():
			return

		boxes = self.get_boxes()

		for b in boxes:
			if max_height < b.box_height:
				max_height = b.box_height
			end_col = start_col + b.box_width
			if end_col > max_col:
				max_col = end_col

			if end_col>self.box_col+self.box_width: 
				start_col   = self.box_col
				start_line += max_height 
				max_height = -1
			b.move(start_line, start_col)
			start_col += b.box_width

		for b in boxes:
			b.draw()

	def work(self):
		if not self.enable:
			return False	
		c = getch()

		if c != ERR and c < 256:
			if c == MY_KEY_DEL:
				if len(self.command) > 0:
					if len(self.command) == 1:
						self.state = CNTRL_LISTEN
					self.command = self.command[:-1]
			else:
				self.command += chr(c)
		
			if c == MY_KEY_ESC:
				self.command = ''
				self.state = CNTRL_LISTEN

			elif self.state == CNTRL_LISTEN:
				if self.command == ':':
					self.state = CNTRL_CMD	
				elif c == ord('\n'):
					os.write(self.source_fd, self.command)
					self.command = ''

			elif self.state == CNTRL_CMD:
				if c == ord('\n'):
					self.command = self.command[1:-1]

					if self.command == 'q':
						raise KeyboardInterrupt
						('ncurses quit')

					elif self.command == 'r':
						LINES, COLS = getmaxyx(Box.stdscr)
						self.resize(LINES, COLS)
						self.draw()

					self.command = ''
					self.state = CNTRL_LISTEN
			
			attron(A_REVERSE) 
			mvaddstr(0, 0, '%s'%self.command)
			attroff(A_REVERSE) 
			clrtoeol()

		for b in self.get_boxes():
			if b.check():
				b.draw()

		for module in self.modules:
			if module.main == True:
				module.work()

		return True
