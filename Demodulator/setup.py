from distutils.core import setup, Extension
import numpy

CostasLoopModule = Extension('CostasLoopC', sources=['Demodulator/CostasLoop.c', 'Demodulator/LockDetector.c', 'Demodulator/Integrator.c', 'Demodulator/LowPass.c'], include_dirs=[numpy.get_include()]) 

setup(ext_modules=[CostasLoopModule])
