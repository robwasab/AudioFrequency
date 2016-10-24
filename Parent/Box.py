from  threading import Thread
from  unicurses import *

BORDER = 2
class Box(Thread):
	def __init__(self, line, col, height, width, debug=False):
		Thread.__init__(self)
		self.box_data = []
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
	
	def box_label(self, line, offset, txt):
		mvwaddstr(self.box_win, line, offset, txt)
		wclrtoeol(self.box_win)

	def box_bar(self, line, offset, size):
		wattron(self.box_win, A_REVERSE) 
		bar_room = self.box_width-2
		bar = ' '*(size if size<bar_room else bar_room)
		mvwaddstr(self.box_win, line, offset, bar)
		wattroff (self.box_win, A_REVERSE)
		wclrtoeol(self.box_win)

	def erase(self):
		werase(self.box_win)
		wrefresh(self.box_win)

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
		self.box_max_msgs = height-len(self.box_data)-BORDER
		if self.box_max_msgs < 0:
			box_max_msgs = 0
		# fix to handle saving old messages
		# when the new size is smaller
		# or when the new size is bigger
		# but I don't expect myself to be changing
		# the size often once it has started up
		self.box_msg_size = 0
		self.box_msgs = ['']*self.box_max_msgs
	
	def box_log(self, msg):
		if msg[-1] == '\n':
			msg = msg[:-1]
		if self.box_msg_size < self.box_max_msgs:
			self.box_msgs[self.box_msg_size] = msg
			self.box_msg_size += 1
		else:
			self.box_msgs[0:-1]=self.box_msgs[1:]
			self.box_msgs[-1]=msg
		self.draw()
	
	def _draw_header(self):
		start  = 1 # border takes up line 0
		offset = 1 # border also takes up col 0
		for line in self.header:
			line[0](start, offset, *line[1:])
			start += 1

	def draw(self):
		self._draw_header()
		# print the messages
		for n in xrange(self.box_msg_size):
			# line to start skips the header
			# in addition to 1 for border
			line = len(self.header)+1+n
			col  = 1
			mvwaddstr(
			self.box_win,line,col,self.box_msgs[n])
		box(self.box_win, 0, 0)
		wrefresh(self.box_win)

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
