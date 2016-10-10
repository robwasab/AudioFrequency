#ifndef __INTEGRATOR_H__
#define __INTEGRATOR_H__

struct Integrator
{
	float (*value)(struct Integrator * i);
	float (*work )(struct Integrator * i, float input);
       	void  (*reset)(struct Integrator * i);	
	void (*dealloc)(struct Integrator * i);
	float lasty;
	float lastx;
	float ki;
};

struct LoopIntegrator
{
	float (*value)(struct LoopIntegrator * i);
	float (*work )(struct LoopIntegrator * i, float input);
       	void  (*reset)(struct LoopIntegrator * i);	
	void (*dealloc)(struct LoopIntegrator * li);
	float last_s3;
	float k1;
	float k2;
	float k3;
	struct Integrator * integrator1;
	struct Integrator * integrator2;
};

typedef struct Integrator Integrator;
typedef struct LoopIntegrator LoopIntegrator;
struct Integrator * Integrator_create(float ki);
struct LoopIntegrator * LoopIntegrator_create(float k1, float k2, float k3);
#endif
