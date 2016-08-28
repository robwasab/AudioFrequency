import select
import pdb
import socket
import Queue
import re
from   pack import length, unpack_payload
from   struct import unpack
import matplotlib.pyplot as plt
import numpy as np
import sys
from   time import time

def process(data):
	payload, data = unpack_payload(data)
	if payload == 'plot' or payload == 'stem':
		print 'PLOT'
		xtype, data = unpack_payload(data)
		ytype, data = unpack_payload(data)
		xdata, data = unpack_payload(data)
		ydata, data = unpack_payload(data)
		xdata = np.fromstring(xdata, dtype = xtype)
		ydata = np.fromstring(ydata, dtype = ytype)
		if len(ydata) == 0:
			if payload == 'plot':
				plt.plot(xdata)
			else:
				plt.stem(xdata)
		else:
			if payload == 'plot':
				plt.plot(xdata, ydata)
			else:
				plt.stem(xdata, ydata)

		plt.show(block = False)

	elif payload == 'figure':
		print 'FIGURE'
		print data
		plt.figure(unpack('I', data)[0])
	
	elif payload == 'title':
		print 'TITLE'
		title, data = unpack_payload(data)
		plt.title(title)
		plt.show(block = False)
	
	
	elif payload == 'xlim':
		print 'XLIM'
		xlim_type, data = unpack_payload(data)
		xlim, data = unpack_payload(data)
		plt.xlim(np.fromstring(xlim, dtype = xlim_type))
		plt.show(block = False)
	
	elif payload == 'ylim':
		print 'YLIM'
		ylim_type, data = unpack_payload(data)
		ylim, data = unpack_payload(data)
		plt.ylim(np.fromstring(ylim, dtype = ylim_type))
		plt.show(block = False)
	
	elif payload == 'xlabel':
		print 'XLABEL'
		xlabel, data = unpack_payload(data)
		plt.xlabel(xlabel)
		plt.show(block = False)
	
	elif payload == 'ylabel':
		print 'YLABEL'
		ylabel, data = unpack_payload(data)
		plt.ylabel(ylabel)
		plt.show(block = False)

	elif payload == 'clf':
		print 'CLEAR FIGURE'
		plt.clf()
		plt.show(block = False)
	
	elif payload == 'cla':
		print 'CLEAR AXIS'
		plt.cla()
		plt.show(block = False)
	
	elif payload == 'subplot':
		print 'SUBPLOT'
		num, data = unpack_payload(data)
		print 'data'
		plt.subplot(int(num))
		plt.show(block = False)

	plt.pause(.1)

def init_server(port_num):
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setblocking(0)
	server.bind(('localhost', port_num))
	server.listen(5)
	return server

def main(port_num):
	plt.ion()
	server = init_server(port_num)
	inputs = [server]
	rx_buffer = {}
	rx_sizes  = {}
	base = time()

	def remove_socket(s):
		inputs.remove(s)
		del rx_buffer[s]
		del rx_sizes[s]
		s.close()

	try:
		while True:
			readable, writable, exceptional = select.select(inputs, [], inputs, 0.1)

			for s in readable:
				# reset timer
				if time() - base > 5.0:
					print 'Quitting Sleep Mode!'
					base = time()
				else:
					base = time()
				if s is server:
					connection, client_address = s.accept()
					print 'Starting new session with ', client_address
					inputs.append(connection)
					rx_buffer[connection] = '' 
				else:
					data = s.recv(1 << 17)

					if data:
						rx_buffer[s] += data
						print 'rx_buffer size: ', len(rx_buffer[s])
						if len(rx_buffer[s]) > 4:
							rx_sizes[s] = length(rx_buffer[s])
							print 'Waiting for %d bytes' % (rx_sizes[s])
						else:
							continue

						if len(rx_buffer[s]) < rx_sizes[s]:
							continue
			
					# interpret empty data as lost connection
					print 'closing session with ', s.getpeername()
					msg = rx_buffer[s][4:] 
					print 'received %d bytes!' % (len(msg))
					process(msg)
					remove_socket(s)

			for s in exceptional:
				print 'Handling exceptional condition for ', s.getpeername()
				remove_socket(s)

			if time() - base > 5.0:
				print 'Sleeping!'
				plt.pause(0.5)

	except KeyboardInterrupt or Exception as e:
		print e
		for i in inputs:
			i.close()
		print 'closing'	
	
if __name__ == '__main__':
	port = 4040 
	if 1 < len(sys.argv):
		port = int(sys.argv[1])
	main(port)
