from   PlotController import PlotController
from   SongLyrics import get_lyric
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
KEY_UP = 65
KEY_DOWN = 66
KEY_RIGHT = 67
KEY_LEFT = 68

class ViewController(Box):
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
			self.selected = self.get_drawable_modules()[0]
			self.selected.box.set_selected(True)
			self.esc_chars = [27,91]
			self.esc_index = 0
			self.plot_controller = PlotController()

		Box.__init__(self,line,col,LINES,COLS)
		self.calc_side()
	
	def get_source(self):
		for module in self.modules:
			if module.__class__.__name__ == 'StdinSource':
				return module
	
	def get_drawable_modules(self):
		drawable = []
		for m in self.modules:
			if m.box is not None:
				drawable.append(m)
		return drawable

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

	
	# Public - Main Thread, only uses dimensions, so no need for mutex locks
	def get_next_box(self, direction):
		box_origin = self.selected.box
		xo = box_origin.box_col
		yo = box_origin.box_line
		if direction == KEY_UP:
			yo -= box_origin.box_height
		elif direction == KEY_DOWN:
			yo += box_origin.box_height
		elif direction == KEY_RIGHT:
			xo += box_origin.box_width
		elif direction == KEY_LEFT:
			xo -= box_origin.box_width

		modules = self.get_drawable_modules()
		min_mag = 1E9
		closest_module = self.selected
		for m in modules:
			y = m.box.box_line
			x = m.box.box_col
			ydelta = y-yo
			xdelta = x-xo
			mag = np.sqrt(ydelta**2+xdelta**2)
			if mag < min_mag:
				closest_module = m
				min_mag = mag
		if closest_module == self.selected:
			return
		else:
			closest_module.box.set_selected(True)
			box_origin.set_selected(False)
			self.selected = closest_module

	def check_esc_seq(self, c):
		if self.esc_index >= len(self.esc_chars):
			self.esc_index = 0
			return True
		if self.esc_chars[self.esc_index] == c:
			self.esc_index += 1
		else:
			self.esc_index = 0
		return False

	def interpret_command(self, command):
		if self.command == 'q':
			raise KeyboardInterrupt('ncurses quit')

		elif self.command == 'r':
			LINES, COLS = getmaxyx(Box.stdscr)
			self.resize(LINES, COLS)
			self.draw()
		elif self.command == 'pon':
			self.plot_controller.add_module(self.selected)

		elif self.command == 'poff':
			self.plot_controller.rm_module(self.selected)

		elif self.command == 'random' or self.command == 'rand':
			os.write(self.source_fd, get_lyric()[:-1])

		elif self.command == 'help' or self.command == '?':
			msgs = self.selected.cmd_info()
			max_info_len = 0
			max_cmd_len = 0
			for msg in msgs:
				cmd = msg[0]
				info = msg[1]
				if len(cmd) > max_cmd_len:
					max_cmd_len = len(cmd)
				if len(info) > max_info_len:
					max_info_len = len(info)

			cmd_infos = []
			for msg in msgs:
				pad = ' ' * (max_cmd_len - len(msg[0]))
				cmd_infos.append(msg[0] + pad + ' : ' + msg[1])

			height = len(msgs) + 4 
			width  = max_cmd_len + max_info_len + 5 
			lines, cols = getmaxyx(Box.stdscr)
			starty = (lines-height)/2
			startx = (cols-width)/2
			msg_box = Box(0,0,0,0)
			msg_box.add_label(self.selected.__class__.__name__)
			msg_box.add_label('')
			for cmd_info in cmd_infos:
				msg_box.add_label(cmd_info)
			msg_box.resize(height, width)
			msg_box.move(starty, startx)
			msg_box.draw()
			while True:
				c = getch()
				if c >= 0 and c < 256:
					break
			msg_box.erase()
			self.draw()
		else:
			self.selected.interpret_cmd(self.command)

	def work(self):
		if not self.enable:
			return False	
		c = getch()

		if self.check_esc_seq(c):
			self.get_next_box(c)

		elif self.esc_index == 0 and c < 256 and c >= 0:
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

					self.interpret_command(self.command)

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

		self.plot_controller.work()
		return True
