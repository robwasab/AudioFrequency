from   Sources.StdinSource   import StdinSource
from   Sinks.StdoutSink      import StdoutSink
from   Sinks.Plotspec        import Plotspec
from   Pulseshape.Pulseshape import Pulseshape
from   Autogain.Autogain     import Autogain
from   Filter.MatchedFilter  import MatchedFilter 
from   TimingRecovery.TimingRecovery import TimingRecovery
from   time import sleep
import matplotlib.pyplot as plt
import traceback

def connect(modules):
	for i in range(0, len(modules)-1):
		modules[i].output = modules[i+1]
		modules[i].fig = i

source = StdinSource()
pshape = Pulseshape (M = 101, beta = 0.5, debug = False)
mfilt  = MatchedFilter(bcoef = pshape.ps, passthrough = True)
trecov = TimingRecovery(M = 101)
sink   = StdoutSink()
specan = Plotspec   (fs = 44.1E3, plt = plt, main = True)

modules = [source, pshape, mfilt, trecov, sink, specan]
connect(modules)

try:
	source.start()
	while True:
		specan.work()
except KeyboardInterrupt:
	print 'quitting all threads!'

except Exception:
	print source.FAIL + 'Got Exception in main!' + source.ENDC
	traceback.print_exc()

source.quit(True)
