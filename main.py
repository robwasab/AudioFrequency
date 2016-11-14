from   Sources.StdinSource   import StdinSource   as StdinS
from   Sources.RandomSource  import RandomSource  as Random
from   Prefix.Prefix         import Prefix        as Prefix
from   Pulseshape.Pulseshape import Pulseshape    as Pulses
from   Filter.FastFilter     import FastFilter    as FastFi
from   Modulator.Modulator   import Modulator     as Modula
from   Noise.Noise           import Noise
from   Filter.Channel        import Channel       as Channe
from   Microphone.Microphone import Microphone    as SimMic
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
from   Controller.ViewController import ViewController
#import matplotlib.pyplot as plt
import numpy as np
import traceback
import pdb
import os

# TODO: Adaptive matched filter? What would the error surface be to that?
# TODO: Additive noise source

fs = 44.1E3
fc = 17E3
fif= 9E3
bw = 500

audio_loopback = False 

def fround(fc):
	n = np.round(float(fs)/float(fc))
	print 'fc: %.1f -> %.1f'%(fc,fs/n)
	return fs/n

def connect(modules):
	for i in range(0, len(modules)-1):
		modules[i].output = modules[i+1]
		modules[i].fig = i
	modules[-1].fig = len(modules)-1

source = StdinS()
prefix = Prefix(bits=9)
pshape = Pulses(M=101, beta = 0.5) 
modula = Modula(fs=fs, fc=fc)
distor = 0.25*np.array([0.1, 0.5, 1.0, -0.6, 0.5, 0.4, 0.3, 0.2, 0.1]) 
channe = Channe(bcoef=distor, passthrough=False)
noise  = Noise (snr_db = 10.0)
speake = Speake(passthrough=False)
microp = Microp(passthrough=True)
simmic = SimMic(passthrough=False)
bandpa = BandPa(fs=fs, fc=fc, bw=bw, taps=2**11, passthrough=False)
mod2if = Modula(fs=fs, fc=(abs(fc-fif))) 
bandif = BandPa(fs=fs, fc=fif,bw=bw, taps=2**11)
autoga = Autoga(fs=fs, M=pshape.M, passthrough=False)
demodu = Demodu(fs=fs, fc=fif)
train_pam = prefix.prepam
train  = (pshape.process(train_pam))
train  = train[(-len(train)/2):(-4*pshape.M)]
equali = Equali(prefix = train, passthrough=False)
mfilte = FastFi(bcoef=pshape.ps)
#interp = Interp(main = False, debug = False, plt=plt, numtaps = 10, L = 2, passthrough=False)
#trecov = Timing(main = False, debug = False, plt=plt, M=pshape.M*interp.L, passthrough=False)
trecov = Timing(M=pshape.M, passthrough=False)
frsync = FrameS(cipher=prefix.cipher, prefix=train_pam, passthrough = False)
stdsin = Stdout()

modules = None

if audio_loopback:
	# Simulates Channel:
	modules = [source, prefix, pshape, modula, channe, noise, simmic, bandpa, mod2if, bandif, autoga, demodu, equali, mfilte, trecov, frsync, stdsin]
else:
	# Uses Microphone:
	modules = [source, prefix, pshape, modula, speake, microp, bandpa, mod2if, bandif, autoga, demodu, equali, mfilte, trecov, frsync, stdsin]

connect(modules)
view_controller = ViewController(modules, 1, 0)
view_controller.draw()

try:
	modules[0].start()
	while True:
		view_controller.work()

except KeyboardInterrupt:
	print 'quitting all threads!'

except Exception:
	modules[0].FAIL + 'Got Exception in main!' + modules[0].ENDC
	traceback.print_exc()

modules[0].quit(True)
