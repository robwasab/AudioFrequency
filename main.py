from   Sources.StdinSource   import StdinSource   as StdinS
from   Sources.RandomSource  import RandomSource  as Random
from   Prefix.Prefix         import Prefix        as Prefix
from   Filter.FastFilter     import FastFilter    as FastFi
from   Pulseshape.Pulseshape import Pulseshape    as Pulses
from   Modulator.Modulator   import Modulator     as Modula
from   Demodulator.Demodulator import Demodulator as Demodu
from   Equalizer.Equalizer           import Equalizer      as Equali
from   Interpolator.Interpolator     import Interpolator   as Interp
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
#ransrc = Random()
prefix = Prefix(main = False, debug = False, bits = 8)
pshape = Pulses(main = False, debug = False, M = 18, beta = 0.5)
modula = Modula(main = False, debug = False, fs = fs, fc = 14.7E3)
distor = [0.5, 1.0, -0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
noloss = [1.0, 0.0]
train  = (pshape.process(prefix.prefix))[:-4*pshape.M]
channe = FastFi(main = False, debug = False, plt = plt, bcoef = distor)
demodu = Demodu(main = False, debug = False, plt = plt, fs = fs, fc = 15.0E3)
equali = Equali(main = False, debug = False, plt = plt, prefix = train, channel=distor, passthrough=False)
mfilte = FastFi(main = False, debug = False, plt = plt, bcoef = pshape.ps)
interp = Interp(main = False, debug = False, plt = plt, numtaps = 20, L = 4)
trecov = Timing(main = False, debug = False, plt = plt, M = pshape.M*interp.L)
frsync = FrameS(main = False, debug = False, plt = plt, prefix = prefix.prefix)
specan = Plotsp(main = True , debug = False, plt = plt, fs = fs)
plot1  = PlotSi(main = True , debug = False, plt = plt, stem = False, persist = False)
plot2  = PlotSi(main = True , debug = False ,plt = plt, stem = False, persist = False)
plot3  = PlotSi(main = True , debug = False, plt = plt, stem = True , persist = False)
stdsin = Stdout(main = True , debug = False )
modules = [source, prefix, pshape, modula, channe, demodu, equali, mfilte, interp, trecov, plot3, frsync, stdsin]
connect(modules)

try:
	modules[0].start()
	while True:
		source.work()
		#plot1.work()
		#plot2.work()
		plot3.work()
		stdsin.work()
		if stdsin.done:
			#stdsin.log('Pass: ' + str(ransrc.data==stdsin.data))
			stdsin.done = False
except KeyboardInterrupt:
	print 'quitting all threads!'

except Exception:
	print modules[0].FAIL + 'Got Exception in main!' + modules[0].ENDC
	traceback.print_exc()

modules[0].quit(True)
