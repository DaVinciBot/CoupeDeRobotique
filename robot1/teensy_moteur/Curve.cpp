#include <iostream>
#include <cmath>

class Curve
{
private:
	float Vi, Vm, Vf;

	float D, D1, D2, D3;

	float T, T1, T2, T3;

	float C1, C3;

public:
	Curve(float intial_velocity, float max_velocity, float final_velocity, float total_distance, float acceleration_distance, float deceleration_distance);
	~Curve() = default;
	float PlannedVelocity(float t);
	float PlannedTotalTime();
};

Curve::Curve(float intial_velocity, float max_velocity, float final_velocity, float total_distance, float acceleration_distance, float deceleration_distance)
{
	this->Vi = intial_velocity;
	this->Vm = max_velocity;
	this->Vf = final_velocity;

	this->D = total_distance;
	this->D1 = acceleration_distance;
	this->D3 = deceleration_distance;
	this->D2 = this->D - this->D1 - this->D3;

	this->T1 = 2 * this->D1 / (this->Vi + this->Vm); // total time of departure phase
	this->T3 = 2 * this->D3 / (this->Vf + this->Vm); // total time of arrival phase
	this->T2 = this->D2 / this->Vm;

	this->T = this->T1 + this->T2 + this->T3;

	this->C1 = (this->Vm - this->Vi) / this->T1; // Departure phase slope
	this->C3 = (this->Vf - this->Vm) / this->T3; // Arrival phase slope
}

float Curve::PlannedTotalTime()
{
	return this->T;
}

float Curve::PlannedVelocity(float t)
{
	if (t > this->PlannedTotalTime())
	{
		return this->Vf;
	}
	else
	{
		float V1 = this->Vi + this->C1 * t;
		float V2 = this->Vm;
		float V3 = this->Vf + this->C3 * (t - this->T);

		return std::min(std::min(V1, V2), V3);
	}
}

int main()
{
	Curve c = Curve(0, 10, 0, 1000, 100, 200);
	float t = 0.0f;
	while (t < c.PlannedTotalTime())
	{
		std::cout << (t == 0.0f ? "" : ",") << c.PlannedVelocity(t);
		t += 0.001f;
	}
	std::cout << std::endl
			  << c.PlannedTotalTime();
	return 0;
}
