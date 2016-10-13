from Microphone.RealMicrophone import Microphone
from Sinks.PlotSink import PlotSink as PlotSi
import matplotlib.pyplot as plt
import numpy as np

def connect(modules):
	for i in range(0, len(modules)-1):
		modules[i].output = modules[i+1]
		modules[i].fig = i
	modules[-1].fig = len(modules)-1

mic = Microphone()
plot1 = PlotSi(main = True, debug = False, plt=plt, stem = False, persist = False)

modules = [mic, plot1]
connect(modules)

try:
	modules[0].start()
	while True:
		plot1.work()

except KeyboardInterrupt:
	print 'quitting all threads!'

except Exception:
	print modules[0].FAIL + 'Got Exception in main!' + modules[0].ENDC
	traceback.print_exc()

modules[0].quit(True)
