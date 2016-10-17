from   Sources.StdinSource   import StdinSource   as StdinS
from   Sources.RandomSource  import RandomSource  as Random
from   Prefix.Prefix         import Prefix        as Prefix
from   Pulseshape.Pulseshape import Pulseshape    as Pulses
from   Filter.FastFilter     import FastFilter    as FastFi
from   Modulator.Modulator   import Modulator     as Modula
from   Filter.Channel        import Channel       as Channe
#from   Microphone.Microphone import Microphone    as Microp
from   Hardware.Hardware     import Microphone    as Microp
from   Hardware.Hardware     import Speaker       as Speake
from   Filter.BandPassFilter import BandPassFilter as BandPa
from   Autogain.Autogain     import Autogain      as Autoga
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
prefix = Prefix(main = False, debug = False, plt=plt, bits=9)
pshape = Pulses(main = False, debug = False, plt=plt, M=101, beta = 0.5) 
modula = Modula(main = False, debug = False, plt=plt, fs=fs, fc = 8820)
distor = np.array([0.1, 0.5, 1.0, -0.6, 0.5, 0.4, 0.3, 0.2, 0.1]) * 0.1
channe = Channe(main = False, debug = False, plt=plt, bcoef=distor, passthrough=False)
speake = Speake(main = False, debug = False, plt=plt, passthrough=False)
microp = Microp(main = False, debug = False, plt=plt, passthrough=False)
bandpa = BandPa(main = False, debug = False, plt=plt, fs = fs, fc = 8820, taps=256, passthrough=False)
autoga = Autoga(main = False, debug = False, plt=plt, fs = fs, M=pshape.M, passthrough=False)
demodu = Demodu(main = False, debug = False, plt=plt, fs = fs, fc = 8820)
train_pam = prefix.prepam
#train  = (pshape.process(train_pam))[:-4*pshape.M]
train  = (pshape.process(train_pam))
train  = train[(-len(train)/2):(-4*pshape.M)]
equali = Equali(main = False, debug = False, plt=plt, prefix = train, passthrough=False)
mfilte = FastFi(main = False, debug = False, plt=plt, bcoef = pshape.ps)
#interp = Interp(main = False, debug = False, plt=plt, numtaps = 10, L = 2, passthrough=False)
#trecov = Timing(main = False, debug = False, plt=plt, M=pshape.M*interp.L, passthrough=False)
trecov = Timing(main = False, debug = False, plt=plt, M=pshape.M, passthrough=False)
frsync = FrameS(main = False, debug = False, plt=plt, cipher=prefix.cipher, prefix=train_pam, passthrough = False)
plot1  = PlotSi(main = True , debug = False, plt=plt, stem = False, persist = False)
plot2  = PlotSi(main = True , debug = False, plt=plt, stem = False, persist = False)
plot3  = PlotSi(main = True , debug = False, plt=plt, stem = True, persist = False)
speca  = Plotsp(main = True , debug = False, plt=plt, stem = True, persist = False, fs = fs)
stdsin = Stdout(main = False)

#modules = [source, prefix, pshape, modula, channe, microp, bandpa, autoga, demodu, equali, mfilte, trecov, plot3, frsync, stdsin]
modules = [source, prefix, pshape, modula, speake, microp, bandpa, autoga, demodu, equali, mfilte, trecov, frsync, stdsin]
connect(modules)

try:
	modules[0].start()
	while True:
		#ransrc.work()
		source.work()
		#prefix.work()
		#pshape.work()
		#modula.work()
		#channe.work()
		#microp.work()
		#bandpa.work()
		#autoga.work()
		#demodu.work()
		#equali.work()
		#mfilte.work()
		#interp.work()
		#trecov.work()
		plot1.work()
		#frsync.work()
		#plot3.work()
		#stdsin.work()
		#if stdsin.done:
		#	stdsin.log('Pass: ' + str(ransrc.data==stdsin.data))
		#	stdsin.done = False
except KeyboardInterrupt:
	print 'quitting all threads!'

except Exception:
	print modules[0].FAIL + 'Got Exception in main!' + modules[0].ENDC
	traceback.print_exc()
modules[0].quit(True)
