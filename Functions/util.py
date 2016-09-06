from   sys import float_info
import numpy as np
import itertools
import pdb

feedback_table = {
 2 : [1,0],
 3 : [2,1],
 4 : [3,2],
 5 : [4,2],
 6 : [5,4],
 7 : [6,5],
 8 : [7,5,4,3],
 9 : [8,4],
10 : [9,6],
11 : [10,8],
12 : [11,10,9,3],
13 : [12,11,10,7],
14 : [13,12,11,1],
15 : [14,13],
16 : [15,14,12,3],
17 : [16,13],
18 : [17,10],
19 : [18,17,16,13]}

def maximumlength(bits):

	def xor(array):
		ret = 0
		for a in array:
			if a > 0:
				ret ^= 1
		return ret
	init_state = np.array([1]*bits)
	state = np.array(init_state) 
	feedback = np.array(feedback_table[bits])
	mlsequ = np.zeros(2**bits-1)
	n = 0
	while True:
		bit = xor(state[feedback])
		state[1:] = state[0:-1]
		state[0]  = bit 
		mlsequ[n] = -1 if bit else 1
		n += 1
		if np.array_equal(init_state, state):
			break
	
	return mlsequ

def letters2pam(s):
	return list(itertools.chain(*[[int(pair[0] + pair[1],2)*2-3 for pair in np.reshape(list('{:08b}'.format(ord(c))),(4,2))] for c in s]))

def quantize(x, alphabet = [-3,-1,1,3]):
	least_error = float_info.max
	closest = alphabet[0]

	for letter in alphabet:
		error = letter - x
		error*= error
		if error < least_error:
			closest = letter
			least_error = error
	return closest

def pam2char(pam):
	return list
if __name__ == '__main__':
	for bits in range(2,20):
		maximumlength(bits)
