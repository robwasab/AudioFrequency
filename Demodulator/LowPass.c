#include "LowPass.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#define PI M_PI

static void init_lp(LowPass * lp, double A, double omega, double sn, double cs, double alpha, double beta)
{
	lp->b0 = (1.0 - cs) / 2.0;
	lp->b1 =  1.0 - cs;
	lp->b2 = (1.0 - cs) / 2.0;
	lp->a0 =  1.0 + alpha;
	lp->a1 = -2.0 * cs;
	lp->a2 =  1.0 - alpha;
}

static float work(LowPass * self, float x)
{
	float y = self->b0*x + self->b1*self->x1 + self->b2*self->x2 - self->a1*self->y1 - self->a2*self->y2;
	self->x2 = self->x1;
	self->x1 = x;
	self->y2 = self->y1;
	self->y1 = y;
	return y;
}

static void reset(LowPass * self)
{
	self->x2 = 0;
	self->x1 = 0;
	self->y2 = 0;
	self->y1 = 0;
}

LowPass * LowPass_create(double fc, double fs)
{
	double Q = 0.7071;
	double A = 1.0;
	double omega = 2.0*PI*fc/fs;
	double sn = sin(omega);
	double cs = cos(omega);
	double alpha = sn/(2.0*Q);
	double beta = sqrt(A+A);
	
	LowPass * lp = malloc(sizeof(LowPass));
	memset(lp, 0, sizeof(LowPass));

	init_lp(lp, A, omega, sn, cs, alpha, beta);
	lp->b0 /= lp->a0;
	lp->b1 /= lp->a0;
	lp->b2 /= lp->a0;
	lp->a1 /= lp->a0;
	lp->a2 /= lp->a0;

	lp->work = work;
	lp->reset = reset;
	return lp;
}
