from   Sources.StdinSource   import StdinSource   as StdinS
from   Sources.RandomSource  import RandomSource  as Random
from   Prefix.Prefix         import Prefix        as Prefix
from   Pulseshape.Pulseshape import Pulseshape    as Pulses
from   Filter.FastFilter     import FastFilter    as FastFi
from   Modulator.Modulator   import Modulator     as Modula
from   Demodulator.Demodulator import Demodulator as Demodu
from   Interpolator.Interpolator     import Interpolator   as Interp
from   Equalizer.Equalizer           import Equalizer      as Equali
from   TimingRecovery.TimingRecovery import TimingRecovery as Timing
from   FrameSync.FrameSync           import FrameSync      as FrameS
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
ransrc = Random(100, main = True)
prefix = Prefix(main = True, debug = False, plt=plt, bits = 8)
pshape = Pulses(main = True, debug = False, M = 18, beta = 0.5) 
modula = Modula(main = True, debug = False, fs = fs, fc = 14.7E3)
distor = [0.5, 1.0, -0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
noloss = [1.0, 0.0]
channe = FastFi(main = True, debug = False, bcoef = distor)
demodu = Demodu(main = True, debug = False, fs = fs, fc = 15.0E3)
train  = (pshape.process(prefix.prepam))[:-4*pshape.M]
equali = Equali(main = True, debug = False, plt=plt, prefix = train, channel=distor, passthrough=False)
mfilte = FastFi(main = True, debug = False, plt=plt, bcoef = pshape.ps)
interp = Interp(main = True, debug = False, plt=plt, numtaps = 20, L = 4)
trecov = Timing(main = True, debug = False, plt=plt, M=pshape.M*interp.L)
frsync = FrameS(main = True, debug = False, plt=plt, cipher = prefix.cipher, prefix = prefix.prepam)
plot1  = PlotSi(main = True, debug = False, plt=plt, stem = False, persist = False)
plot2  = PlotSi(main = True, debug = False, plt=plt, stem = True, persist = False)
stdsin = Stdout(main = True)
modules = [source, prefix, pshape, modula, channe, demodu, plot1, equali, mfilte, interp, trecov, plot2, frsync, stdsin]
connect(modules)
try:
	modules[0].start()
	while True:
		#ransrc.work()
		source.work()
		prefix.work()
		pshape.work()
		modula.work()
		channe.work()
		demodu.work()
		plot1.work()
		equali.work()
		mfilte.work()
		interp.work()
		plot1.work()
		trecov.work()
		plot2.work()
		frsync.work()
		stdsin.work()
		plt.show()

except KeyboardInterrupt:
	print 'quitting all threads!'

except Exception:
	print modules[0].FAIL + 'Got Exception in main!' + modules[0].ENDC
	traceback.print_exc()

modules[0].quit(True)
