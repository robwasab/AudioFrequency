from   Sources.StdinSource   import StdinSource   as StdinS
from   Sources.RandomSource  import RandomSource  as Random
from   Prefix.Prefix         import Prefix        as Prefix
from   Pulseshape.Pulseshape import Pulseshape    as Pulses
from   Modulator.Modulator   import Modulator     as Modula
from   Demodulator.Demodulator import Demodulator as Demodu
from   Filter.FastFilter       import FastFilter    as FastFi
from   TimingRecovery.TimingRecovery import TimingRecovery as Timing
from   FrameSync.FrameSync           import FrameSync      as FrameS
from   Sinks.StdoutSink              import StdoutSink     as Stdout
from   Sinks.Plotspec                import Plotspec       as Plotsp
from   Sinks.PlotSink                import PlotSink       as PlotSi
import matplotlib.pyplot as plt
import numpy as np
import traceback
import pdb

fs = 44.1E3

def fround(fc):
	n = np.round(float(fs)/float(fc))
	return fs/n


def connect(modules):
	for i in range(0, len(modules)-1):
		modules[i].output = modules[i+1]
		modules[i].fig = i
	modules[-1].fig = len(modules)-1

source = StdinS(main = True)
ransrc = Random()
prefix = Prefix(main = False, debug = False )
pshape = Pulses(main = False, debug = False, M = 101, beta = 0.5)
modula = Modula(main = False, debug = False, fs = fs, fc = 10E3)
demodu = Demodu(main = False, debug = False, fs = fs, fc = fround(10E3), plt = plt)
mfilte = FastFi(main = False, debug = False, bcoef = pshape.ps)
trecov = Timing(main = False, debug = False, M = 101)
frsync = FrameS(main = False, debug = False, prefix = prefix.prefix)
stdsin = Stdout(main = True , debug = False )
specan = Plotsp(main = True , debug = False, plt = plt, fs = fs)
plot1  = PlotSi(main = True , debug = False, plt = plt, stem = False, persist = False)
plot2  = PlotSi(main = True , debug = False ,plt = plt, stem = False, persist = False)
plot3  = PlotSi(main = True , debug = False, plt = plt, stem = False, persist = False)
modules = [ransrc, prefix, pshape, modula, demodu, mfilte, trecov, plot1, frsync, stdsin]
connect(modules)

try:
	modules[0].start()
	while True:
		#source.work()
		plot1.work()
		stdsin.work()
		if stdsin.done:
			stdsin.log('Pass: ' + str(ransrc.data==stdsin.data))
			stdsin.done = False
except KeyboardInterrupt:
	print 'quitting all threads!'

except Exception:
	print modules[0].FAIL + 'Got Exception in main!' + modules[0].ENDC
	traceback.print_exc()

modules[0].quit(True)
