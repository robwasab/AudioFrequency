#include <Python.h>
#include "LowPass.h"
#include "LockDetector.h"
#define sq(x) (x*x)
typedef struct LockDetector LockDetector;

int work(LockDetector * self, float in_phase, float qu_phase)
{
	in_phase = 
	self->in_phase_lp->work(self->in_phase_lp, sq(in_phase));
	qu_phase = 
	self->qu_phase_lp->work(self->qu_phase_lp, sq(qu_phase));
	if (in_phase > self->thresh && qu_phase < self->thresh)
		return true;
	else
		return false;
}

void reset(LockDetector * self)
{
	self->in_phase_lp->reset(self->in_phase_lp);
	self->qu_phase_lp->reset(self->qu_phase_lp);
}

void dealloc(LockDetector * self)
{
	free(self->in_phase_lp);
	free(self->qu_phase_lp);
	free(self);
}

LockDetector * LockDetector_create(float fs)
{
	LockDetector * lock = malloc(sizeof(LockDetector));
	memset(lock, 0, sizeof(LockDetector));
	lock->in_phase_lp = LowPass_create(10.0, fs);
	lock->qu_phase_lp = LowPass_create(10.0, fs);
	lock->thresh = 1E-1;
	lock->reset = reset;
	lock->work = work;
	lock->dealloc = dealloc;
	return lock;
}
