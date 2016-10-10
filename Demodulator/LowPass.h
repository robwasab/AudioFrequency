#ifndef __LOW_PASS_H__
#define __LOW_PASS_H__

struct LowPass
{
	float a0;
	float a1;
	float a2;
	float b0;
	float b1;
	float b2;
	float x1;
	float x2;
	float y1;
	float y2;
	float (*work)(struct LowPass * self, float x);
	void (*reset)(struct LowPass * self);
};

typedef struct LowPass LowPass;
LowPass * LowPass_create(double fc, double fs);

#endif
