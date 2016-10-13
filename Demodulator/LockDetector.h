#ifndef __LOCK_DETECTOR_H__
#define __LOCK_DETECTOR_H__
#include <stdint.h>
#include <stdbool.h>

struct LockDetector 
{
	LowPass * in_phase_lp;
	LowPass * qu_phase_lp;
	float thresh;
	void (*reset)(struct LockDetector * self);
	int (*work)(struct LockDetector * self, float in_phase, float qu_phase);
	void (*dealloc)(struct LockDetector * self);
};
typedef struct LockDetector LockDetector;
LockDetector * LockDetector_create(float fs);
#endif
