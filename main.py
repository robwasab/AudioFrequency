from   Sources.StdinSource   import StdinSource
from   Sources.RandomSource  import RandomSource
from   Prefix.Prefix         import Prefix
from   Pulseshape.Pulseshape import Pulseshape
from   Autogain.Autogain     import Autogain
from   Filter.MatchedFilter  import MatchedFilter 
from   Filter.FastFilter     import FastFilter
from   TimingRecovery.TimingRecovery import TimingRecovery
from   Sinks.StdoutSink import StdoutSink
from   Sinks.Plotspec   import Plotspec
from   Sinks.PlotSink   import PlotSink
import matplotlib.pyplot as plt
from   time import sleep
import traceback
import pdb

def connect(modules):
	for i in range(0, len(modules)-1):
		modules[i].output = modules[i+1]
		modules[i].fig = i
	modules[-1].fig = len(modules)-1

source = StdinSource()
#ransrc = RandomSource()
prefix = Prefix()
pshape = Pulseshape (M = 101, beta = 0.5, debug = False)
mfilt  = FastFilter(bcoef = pshape.ps)
trecov = TimingRecovery(M = 101)
sink   = StdoutSink()
specan = Plotspec(fs = 44.1E3, plt = plt, main = True)
stem1  = PlotSink(plt = plt, stem = False, main = True)
stem2  = PlotSink(plt = plt, stem = False, main = True)

modules = [source, prefix, pshape, mfilt, stem1, trecov, stem2, sink]
connect(modules)
try:
	modules[0].start()
	while True:
		#specan.work()
		stem1.work()
		stem2.work()
except KeyboardInterrupt:
	print 'quitting all threads!'

except Exception:
	print modules[0].FAIL + 'Got Exception in main!' + modules[0].ENDC
	traceback.print_exc()

modules[0].quit(True)
