from struct import pack, unpack
import numpy as np

def length(data):
	size, = unpack('I', data[0:4])
	return size

def prefix(array):
	return pack( 'I', len(array))

def figure(fig_num):
	payload = prefix('figure') + 'figure' + pack('I',fig_num)
	return prefix(payload) + payload

def lim(cmd, low, high):
	lim = np.array([low, high])
	payload_type = str(lim.dtype)
	lim = lim.tostring()
	payload = prefix(lim) + lim
	payload = prefix(payload_type) + payload_type + payload
	payload = prefix(cmd) + cmd + payload 
	payload = prefix(payload) + payload
	return payload

def xlim(low, high):
	return lim('xlim', low, high)

def ylim(low, high):
	return lim('ylim', low, high)

def label(cmd, l):
	payload = prefix(cmd) + cmd + prefix(l) + l
	return prefix(payload) + payload

def ylabel(l):
	return label('ylabel', l)

def xlabel(l):
	return label('xlabel', l)

def title(l):
	return label('title', l)

def plot(xdata, ydata, cmd = 'plot'):
	xtype = str(xdata.dtype)
	ytype = str(ydata.dtype)
	xdata = xdata.tostring()
	ydata = ydata.tostring()
	payload = ydata
	payload = prefix(ydata) + payload
	payload = xdata + payload
	payload = prefix(xdata) + payload
	payload = ytype + payload
	payload = prefix(ytype) + payload
	payload = xtype + payload
	payload = prefix(xtype) + payload
	payload = cmd + payload
	payload = prefix(cmd) + payload
	payload = prefix(payload) + payload
	return payload

def command(cmd):
	payload = prefix(cmd) + cmd
	return prefix(payload) + payload

def stem(xdata, ydata):
	plot(xdata, ydata, 'stem')

def unpack_payload(data):
	size = length(data) 
	payload = data[4:4+size]
	remainder = data[4+size:]
	return (payload, remainder)

