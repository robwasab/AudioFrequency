import numpy as np
import matplotlib.pyplot as plt

def test_modulator():
	from Modulator.Modulator import Modulator
	# test with data that has integer periods in terms of fc

	mod = Modulator(fs = 44.1E3, fc = 10E3, debug = False)
	for cycles in range(1,1000):
		ftest = mod.fc/cycles
	
		for x in range (0,4):
			# algebra:
			# nsamp = mod.fs/mod.fc*10

			for y in range(0, 4):
				mod.reset()
				print '* * * starting * * *'
		
				nsamp = np.arange(0, y+int(mod.fs/ftest))
				waveform = np.cos(2.0*np.pi*ftest*nsamp/mod.fs)

				answer   = waveform * np.sin(2.0*np.pi*mod.fc*np.arange(0,len(waveform))/mod.fs)

				half = len(waveform)/2 + x

				print 'computing chunk [%d:%d]'%(0,half)
				mod_data = mod.process(waveform[0:half])
				print 'computing chunk [%d:%d]'%(half, len(waveform))
				mod_data = np.append(mod_data,mod.process(waveform[half:]))
	
				error = max(np.abs(answer-mod_data))
				print 'x: %d y: %d e: %f'%(x,y,error)

				if error > 1E-6:
					plt.gcf().clf()

					plt.subplot(311)
					plt.stem(answer)

					plt.subplot(312)
					plt.stem(mod_data)

					plt.subplot(313)
					plt.stem(answer-mod_data)
					plt.ylim((-1,1))

					plt.show()

def test_demodulator():
	from Demodulator.Demodulator import Demodulator
	
	demod = Demodulator(fc = 14E3, debug = True)

# It passes... I'm convinced..
#test_modulator()

test_demodulator()
