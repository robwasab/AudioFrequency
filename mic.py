import matplotlib.pyplot as plt
import numpy as np

mic = np.loadtxt('microphone_data2.gz')

plt.plot(mic)
plt.show()
