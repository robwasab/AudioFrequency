from   threading import Lock
from   unicurses import *
import atexit
import pdb
import sys

def quit_ncurses():
	refresh()
	endwin()

BORDER = 2
class Box(object):
	init_ncurses = True
	stdscr = -1
	def __init__(self, line, col, height, width):
		if Box.init_ncurses and len(sys.argv) > 1:
			stdscr = initscr()
			if has_colors() != ERR:
				start_color()
				use_default_colors()
			Box.stdscr = stdscr
			clear()
			noecho()
			cbreak()
			nodelay(Box.stdscr, True)
			curs_set(0)
			refresh()
			atexit.register(quit_ncurses)
			Box.init_ncurses = False

	# Dimension Properties shall only be accessed from the main thread
	# Information Properties shall have multi thread access
	# Therefore Dimension Properties will not have a mutex lock
	# Information Properties will have a mutex lock

		self.box_offset = 1
		self.box_max_msgs = 0
		self.box_msg_size = 0
		self.box_msgs = []
		self.box_line = line 
		self.box_col  = col
		self.box_height = height
		self.box_width  = width
		self.box_win = newwin(
		self.box_height, 
		self.box_width,
		self.box_line, 
		self.box_col)
		self.box_header = []
		self.box_lock = Lock()
		self.box_update = False
		self.box_selected = False
		self.box_txt_red = 0x1
		self.box_txt_grn = 0x2
		self.box_txt_blu = 0x3
		self.box_txt_ylw = 0x4
		self.box_txt_mga = 0x5
		init_pair(self.box_txt_red, COLOR_RED  , -1)
		init_pair(self.box_txt_grn, COLOR_GREEN, -1)
		init_pair(self.box_txt_blu, COLOR_BLUE , -1)
		init_pair(self.box_txt_ylw, COLOR_YELLOW, -1)
		init_pair(self.box_txt_mga, COLOR_MAGENTA, -1)
	
	# Private
	# Will only be called in draw()
	def draw_label(self, line, offset, txt):
		mvwaddstr(self.box_win, line, offset, txt)
		wclrtoeol(self.box_win)

	# Private
	# Will only be called in draw()
	def draw_bar(self, line, offset, size):
		wattron(self.box_win, A_REVERSE) 
		bar_room = self.box_width-2
		bar = ' '*(size if size<bar_room else bar_room)
		mvwaddstr(self.box_win, line, offset, bar)
		wattroff (self.box_win, A_REVERSE)
		wclrtoeol(self.box_win)

	# Private
	# Helper function see add_label, add_bar
	def header_add(self, draw_func, *args):
		header = [draw_func]
		for a in args:
			header.append(a)
		self.box_header.append(header)
		index = len(self.box_header)-1
		return index 

	# Public - Main Thread
	# Only use during Module initialization on main thread
	def add_label(self, txt):
		return self.header_add(self.draw_label, txt)

	# Public - Main Thread
	# Only use during Module initialization on main thread
	def add_bar(self, size):
		return self.header_add(self.draw_bar, size)

	# Public - Random Access 
	# Module calls this to modify a display property
	def notify(self, index, new_arg):
		self.box_lock.acquire()
		self.box_header[index][1] = new_arg
		self.box_update = True
		self.box_lock.release()

	# Public - Main Thread
	# View Controller calls this to see if Box has been modified
	# self.box_update property is shared between threads
	def check(self):
		self.box_lock.acquire()
		ret = False
		ret = self.box_update
		self.box_update = False
		self.box_lock.release()
		return ret

	# Private
	def erase(self):
		werase(self.box_win)
		wrefresh(self.box_win)

	# Public - Main Thread
	# View Controller calls this when it resizes
	def resize(self, height, width):
		self.erase()
		delwin(self.box_win)
		self.box_width = width
		self.box_height = height
		self.box_win = newwin(
		self.box_height, 
		self.box_width, 
		self.box_line, 
		self.box_col)
		self.box_max_msgs = height-len(self.box_header)-BORDER
		if self.box_max_msgs < 0:
			box_max_msgs = 0
		# fix to handle saving old messages
		# when the new size is smaller
		# or when the new size is bigger
		# but I don't expect myself to be changing
		# the size often once it has started up
		self.box_lock.acquire()
		self.box_msg_size = 0
		self.box_msgs = ['']*self.box_max_msgs
		self.box_lock.release()

	# Public - Random Access
	# Called from Module, which will modify the 
	# self.box_msgs, self.box_msg_size variables
	def box_log(self, msg):
		self.box_lock.acquire()
		if msg[-1] == '\n':
			msg = msg[:-1]
		
		if len(msg) > self.box_max_msgs*(self.box_width-2):
			msg = msg[:self.box_max_msgs]

		while len(msg) > 0:
			end = self.box_width-2
			if len(msg) <= end:
				end = len(msg)
			else:
				for n in xrange(end, self.box_width/2, -1):
					if msg[n] == ' ':
						end = n
						break
			
			if self.box_msg_size < self.box_max_msgs:
				self.box_msgs[self.box_msg_size] = msg[:end]
				self.box_msg_size += 1
			else:
				self.box_msgs[0:-1]=self.box_msgs[1:]
				self.box_msgs[-1]=msg[:end]
			msg = msg[end:]
		self.box_update = True
		self.box_lock.release()

	# Public - Main Thread
	# Nothing can interrupt it while it is drawing
	def draw(self):
		self.box_lock.acquire()
		start = 1 # boarder takes up line 0
		offset= 1 # boarder also takes up col 0
		for line in self.box_header:
			line[0](start, offset, *line[1:])
			start += 1

		for n in xrange(self.box_msg_size):
			# line to start skips the header
			# in addition to 1 for border
			line = len(self.box_header)+1+n
			col  = 1
			mvwaddstr(
			self.box_win,line,col,self.box_msgs[n])
			wclrtoeol(self.box_win)
		if self.box_selected:
			wattron(self.box_win, A_BOLD)
			wattron(self.box_win, COLOR_PAIR(self.box_txt_grn))
			box(self.box_win, 0, 0)
			wattroff(self.box_win, A_BOLD)
			wattroff(self.box_win, COLOR_PAIR(self.box_txt_grn))
		else:
			box(self.box_win, 0, 0)

		wrefresh(self.box_win)
		self.box_lock.release()

	# Public - Main Thread
	# Only modifies dimensions. Only main thread relies on
	# dimensions because of drawing, no lock
	def move(self, line, col):
		self.erase()
		delwin(self.box_win)
		self.box_line = line
		self.box_col = col
		self.box_win = newwin(
		self.box_height, 
		self.box_width, 
		self.box_line, 
		self.box_col)
	
	# Public - Main Thread
	def set_selected(self, selected):
		self.box_lock.acquire()
		self.box_selected = selected
		self.box_update = True
		self.box_lock.release()
