#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <Python.h>
#include <numpy/arrayobject.h>
#include <math.h>
#include "Integrator.h"
#include "LowPass.h"
#include "LockDetector.h"
#define PI M_PI

static double fc, fs, F, gain;
static float last_vco_phase;
static float rc_tau;
static float rc_constant;
static float ref;
static Integrator * vco_integrator;
static LoopIntegrator * phase_integrator;
static LowPass * ilp;
static LowPass * qlp;
static LowPass * ilp_signal;
static LowPass * qlp_signal;
static LowPass * freq_filter;
static LowPass * input_thresh_lp;
static LockDetector * lock_detector;

static PyObject * init(PyObject * self, PyObject * args)
{
	if (!PyArg_ParseTuple(args, "dd", &fc, &fs))
		return NULL;
		
	F = fc/fs;
	vco_integrator = Integrator_create(F);
	
	// for estimating the frequency
	last_vco_phase = 0;

	// Special 2nd order integrator for tracking ramping phase
	float k1 = 1.0/3.0;
      	float k2 = 1.0/4.0;
	float k3 = 1.0/16.0;
	phase_integrator = LoopIntegrator_create(k1, k2, k3);

	// Low Pass filters for generating the error signal
	ilp = LowPass_create(fc, fs);
	qlp = LowPass_create(fc, fs);

	// Low Pass Filters for filtering the output signal
	ilp_signal = LowPass_create(fc > 2E3 ? 2E3 : fc, fs);
	qlp_signal = LowPass_create(fc > 2E3 ? 2E3 : fc, fs);
	lock_detector = LockDetector_create(fs);
	return Py_None;
}

inline static float work(float input)
{
	static int locked = 0;
	static float real_input;
	real_input = input;
	if (input > 1.0)
		input = 1.0;
	else if (input < -1.0)
		input = -1.0;

	// Phase Generator
	// vco_phase is a constantly increasing phase value
	double vco_phase = 2.0*PI*(phase_integrator->value(phase_integrator) + vco_integrator->value(vco_integrator));

	// Oscillator
	double cos_vco = cos(vco_phase);
	double sin_vco =-sin(vco_phase);

	// Error Generator
	float in_phase = ilp->work(ilp, input*cos_vco);
	float qu_phase = qlp->work(qlp, input*sin_vco);

	// Update Loop Integrators
	phase_integrator->work(phase_integrator, in_phase*qu_phase);
	vco_integrator->work(vco_integrator, 1.0);

	// Downconvert analog
	float in_phase_signal = 2.0*ilp_signal->work(ilp_signal, real_input*cos_vco);

	float qu_phase_signal = 2.0*qlp_signal->work(qlp_signal, real_input*sin_vco);

	locked = lock_detector->work(lock_detector, in_phase_signal, qu_phase_signal);

	static int foo = 0;
	static int bar = 0;
	if (locked) {
		if (!foo) {
			//fprintf(stderr, "Locked...\r\n");
			foo = 1;
		}
		bar = 0;
	}
	else {
		if (!bar) {
			//fprintf(stderr, "Unlocked...\r\n");
			bar = 1;
		}
		foo = 0;
	}
	
	return 0.7*in_phase_signal;	
}

static PyObject * process(PyObject * self, PyObject * args)
{
	PyArrayObject * in_array;
	PyObject * out_array;
	NpyIter * in_iter;
	NpyIter * out_iter;
	NpyIter_IterNextFunc * in_iternext;
	NpyIter_IterNextFunc * out_iternext;

	if (!PyArg_ParseTuple(args, "O!", &PyArray_Type, &in_array))
		return NULL;

	out_array = PyArray_NewLikeArray(in_array, NPY_ANYORDER, NULL, 0);
	if (out_array == NULL)
		return NULL;

	in_iter = NpyIter_New(in_array, NPY_ITER_READONLY, NPY_KEEPORDER,
			NPY_NO_CASTING, NULL);

	if (in_iter == NULL)
		goto fail;

	out_iter = NpyIter_New((PyArrayObject *) out_array, NPY_ITER_READWRITE,
			NPY_KEEPORDER, NPY_NO_CASTING, NULL);

	if (out_iter == NULL) {
		NpyIter_Deallocate(in_iter);
	}

	in_iternext = NpyIter_GetIterNext(in_iter, NULL);
	out_iternext = NpyIter_GetIterNext(out_iter, NULL);
	if (in_iternext == NULL || out_iternext == NULL) {
		NpyIter_Deallocate(in_iter);
		NpyIter_Deallocate(out_iter);
		goto fail;
	}

	double ** in_dataptr  =  (double **)NpyIter_GetDataPtrArray(in_iter);
	double ** out_dataptr =  (double **)NpyIter_GetDataPtrArray(out_iter);

	switch (PyArray_TYPE(in_array))
	{
		case NPY_FLOAT32:
			do {
				**((float **)out_dataptr) = (float) work(**((float **)in_dataptr));
			} while (in_iternext(in_iter) && out_iternext(out_iter));
			break;
		case NPY_FLOAT64:
			do {
				**out_dataptr = work(**in_dataptr);
			} while (in_iternext(in_iter) && out_iternext(out_iter));
			break;
		default:
			printf("unknown type...");
			return NULL;
	}
	NpyIter_Deallocate(in_iter);
	NpyIter_Deallocate(out_iter);
	Py_INCREF(out_array);
	return out_array;

fail:
	Py_XDECREF(out_array);
	return NULL;
}

static PyMethodDef methods[] = 
{
	{"process", process, METH_VARARGS, ""},
	{"init", init, METH_VARARGS, ""},
	{NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initCostasLoopC(void)
{
	(void) Py_InitModule("CostasLoopC", methods);
	import_array();
}

