import numpy as np
import itertools
from   sys import float_info

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
