import socket
import sys
import numpy as np
from   settings import PORT 
import pdb
import pack
import sys

FAIL = '\033[91m'
ENDC = '\033[0m'

class PlotClient(object):
	def __init__(self, port):
		self.server_address  = ('localhost', port)

	def wait_for_server(self, server):
		try:
			while True:
				data = server.recv(1024)
				if not data:
					break
		except KeyboardInterrupt:
			pass
		server.close()

	def send_payload(self, payload):
		plotter = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		plotter.setblocking(0)
		plotter.settimeout(10.0)
		try:
			plotter.connect(self.server_address)
		except Exception:
			print FAIL + 'Could not connect to server' + ENDC
			return

		plotter.send(payload)
		self.wait_for_server(plotter)

	def plot(self, x, y=[], cmd = 'plot'):
		x = np.array(x)
		y = np.array(y)
		self.send_payload(pack.plot(x,y,cmd))

	def figure(self, n):
		self.send_payload(pack.figure(n))

	def xlim(self, l, h):
		self.send_payload(pack.xlim(l,h))

	def ylim(self, l,h):
		self.send_payload(pack.ylim(l,h))

	def xlabel(self, l):
		self.send_payload(pack.xlabel(l))

	def ylabel(self, l):
		self.send_payload(pack.ylabel(l))

	def title(self, t):
		self.send_payload(pack.title(t))

	def stem(self,x, y=[]):
		self.plot(x,y,'stem')

	def clf(self):
		self.send_payload(pack.command('clf'))

	def cla(self):
		self.send_payload(pack.command('cla'))
	
	def subplot(self, num):
		self.send_payload(pack.subplot(num))

