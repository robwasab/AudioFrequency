from   Sources.StdinSource   import StdinSource
from   Sources.RandomSource  import RandomSource
from   Prefix.Prefix         import Prefix
from   Pulseshape.Pulseshape import Pulseshape
from   Autogain.Autogain     import Autogain
from   Filter.MatchedFilter  import MatchedFilter 
from   Filter.FastFilter     import FastFilter
from   TimingRecovery.TimingRecovery import TimingRecovery
from   FrameSync.FrameSync import FrameSync
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

source = StdinSource(main = True)
#ransrc = RandomSource()
prefix = Prefix()
pshape = Pulseshape (M = 101, beta = 0.5, debug = False)
mfilt  = FastFilter(bcoef = pshape.ps)
trecov = TimingRecovery(M = 101)
fsync  = FrameSync(prefix = prefix.prefix)
sink   = StdoutSink()
specan = Plotspec(fs = 44.1E3, plt = plt,  main = True)
plot1  = PlotSink(plt = plt, stem = False, main = True, persist = False)
plot2  = PlotSink(plt = plt, stem = True,  main = True, persist = True)
plot3  = PlotSink(plt = plt, stem = False, main = True)
modules = [source, prefix, pshape, mfilt, trecov, plot1, fsync, sink]
connect(modules)
try:
	modules[0].start()
	while True:
		#specan.work()
		source.work()
		plot1.work()
		#plot2.work()
		#plot3.work()
except KeyboardInterrupt:
	print 'quitting all threads!'

except Exception:
	print modules[0].FAIL + 'Got Exception in main!' + modules[0].ENDC
	traceback.print_exc()

modules[0].quit(True)
