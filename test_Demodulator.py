from   Sources.StdinSource   import StdinSource   as StdinS
from   Sources.RandomSource  import RandomSource  as Random
from   Prefix.Prefix         import Prefix        as Prefix
from   Pulseshape.Pulseshape import Pulseshape    as Pulses
from   Filter.MatchedFilter  import MatchedFilter as MatchF
from   Modulator.Modulator   import Modulator     as Modula
from   Demodulator.Demodulator import Demodulator as Demodu
from   Filter.FastFilter     import FastFilter    as FastFi
from   Sinks.StdoutSink import StdoutSink         as Stdout
from   Sinks.Plotspec   import Plotspec           as Plotsp
from   Sinks.PlotSink   import PlotSink           as PlotSi
import matplotlib.pyplot as plt
import numpy as np
import traceback
import pdb

fs = 44.1E3

def fround(fc):
	n = np.round(float(fs)/float(fc))
	print 'fc: %.1f -> %.1f'%(fc,fs/n)
	return fs/n

def connect(modules):
	for i in range(0, len(modules)-1):
		modules[i].output = modules[i+1]
		modules[i].fig = i
	modules[-1].fig = len(modules)-1

source = StdinS(main = True)
#ransrc= Random()
prefix = Prefix(main = True, debug = False )
pshape = Pulses(main = True, debug = False, M = 101, beta = 0.5)
mfilte = FastFi(main = True, debug = False, bcoef = pshape.ps)
class TesMod(Modula):
	def __init__(self, *args, **kwargs):
		kwargs['fc'] = 4E3 #Dummy
		Modula.__init__(self,*args, **kwargs)
		kwargs['fc'] = 6E3
		self.mod1 = Modula(*args, **kwargs) 
		kwargs['fc'] = 7E3
		self.mod2 = Modula(*args, **kwargs)
		kwargs['fc'] = 6E3
		self.mod3 = Modula(*args, **kwargs)
		kwargs['fc'] = 5E3
		self.mod4 = Modula(*args, **kwargs)
	
	def process(self, data):
		data1 = np.copy(data)
		data2 = np.copy(data)
		data3 = np.copy(data)
		data4 = np.copy(data)
		data1 = self.mod1.process(data1)
		data2 = self.mod2.process(data2)
		data3 = self.mod3.process(data3)
		data4 = self.mod4.process(data4)
		return np.append(data1, np.append(data2, np.append(data3, data4))) 

modula = TesMod(main = True, debug = False, fs = fs)

demodu = Demodu(main = True, debug = False, fs = fs, fc = 5E3, plt = plt)
stdsin = Stdout(main = True, debug = False )
specan = Plotsp(main = True, debug = True , fs = fs, plt = plt)
plot1  = PlotSi(main = True, debug = False, plt = plt, stem = False, persist = False)
plot2  = PlotSi(main = True, debug = True , plt = plt, stem = False, persist = False)
plot3  = PlotSi(main = True, debug = False, plt = plt, stem = False, persist = False)
modules = [source, prefix, pshape, mfilte, modula, plot1, demodu, plot2]
connect(modules)
try:
	modules[0].start()
	while True:
		source.work()
		prefix.work()
		pshape.work()
		mfilte.work()
		modula.work()
		plot1.work()
		demodu.work()
		plot2.work()
		#specan.work()

except KeyboardInterrupt:
	print 'quitting all threads!'

except Exception:
	print modules[0].FAIL + 'Got Exception in main!' + modules[0].ENDC
	traceback.print_exc()

modules[0].quit(True)
