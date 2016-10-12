import matplotlib.pyplot as plt
import numpy as np

tau = 0.001
fs = 44.1E3

sim_len = 1000
vc = 0.1
out = np.zeros(sim_len)
out[0] = 0  
for n in range(1, sim_len):
	out[n] = (vc + tau*fs*out[n-1])/(tau*fs+1)

plt.plot(out)
plt.show()
