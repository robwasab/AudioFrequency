from Functions.util import maximumlength
import matplotlib.pyplot as plt
import numpy as np
from   numpy.fft import fft, ifft
from   FrameSync import FrameSync

prefix = maximumlength(8)
fsync = FrameSync(prefix = prefix, plt = plt, main = True)
rx = np.append(np.zeros(128+64), np.append(prefix,np.zeros(64)))
fsync.process(rx)

prefix = np.append(np.fliplr([prefix])[0], np.zeros(256))
correl = ifft(fft(prefix)*fft(rx)).real/256.0
plt.stem(correl, 'r')
plt.stem(rx)
#plt.show()

