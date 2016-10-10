#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "Integrator.h"


static float value(Integrator * self)
{
	return self->lasty;
}

static float work(Integrator * self, float input)
{
	self->lasty = self->ki*self->lastx + self->lasty;
	self->lastx = input;
	return self->lasty;
}

static void reset(Integrator * self)
{
	self->lasty = 0.0;
	self->lastx = 0.0;
}

static void dealloc(Integrator * self)
{
	free(self);
}

static float li_value(LoopIntegrator * self)
{
	return self->last_s3;
}

static float li_work(LoopIntegrator * self, float s1)
{
	Integrator * int1 = self->integrator1;
	Integrator * int2 = self->integrator2;
	self->last_s3 = self->k1*s1 + int1->work(int1, s1*self->k1*self->k2+int2->work(int2, s1*self->k1*self->k2*self->k3));
	return self->last_s3;
}

static void li_reset(LoopIntegrator * self)
{
	self->last_s3 = 0;
	self->integrator1->reset(self->integrator1);
	self->integrator2->reset(self->integrator2);
}

void li_dealloc(LoopIntegrator * self)
{
	free(self->integrator1);
	free(self->integrator2);
	free(self);
}

Integrator * Integrator_create(float ki)
{
	Integrator * i = malloc(sizeof(Integrator));
	memset(i, 0, sizeof(Integrator));
	i->ki = ki;
	i->value = value;
	i->work = work;
	i->reset = reset;
	i->dealloc = dealloc;
	return i;
}

LoopIntegrator * LoopIntegrator_create(float k1, float k2, float k3)
{
	LoopIntegrator * li = malloc(sizeof(LoopIntegrator));
	memset(li, 0, sizeof(LoopIntegrator));
	li->k1 = k1;
	li->k2 = k2;
	li->k3 = k3;
	li->integrator1 = Integrator_create(1.0);
	li->integrator2 = Integrator_create(1.0);
	li->value = li_value;
	li->work = li_work;
	li->reset = li_reset;
	li->dealloc = li_dealloc;
	return li;
}
