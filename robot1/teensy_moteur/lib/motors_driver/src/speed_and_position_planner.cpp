#include <speed_and_position_planner.h>


SpeedPositionPlanner::SpeedPositionPlanner(
		float max_speed, 
		float total_distance, 
		float acceleration_distance, float deceleration_distance,
		float intial_speed, float final_speed 
	)
{
	this->Si = intial_speed;
	this->Sm = max_speed;
	this->Sf = final_speed;

	this->D = total_distance;
	this->D1 = acceleration_distance;
	this->D3 = deceleration_distance;
	this->D2 = this->D - this->D1 - this->D3;

	this->T1 = 2 * this->D1 / (this->Si + this->Sm); // total time of departure phase
	this->T3 = 2 * this->D3 / (this->Sf + this->Sm); // total time of arrival phase
	this->T2 = this->D2 / this->Sm;

	this->T = this->T1 + this->T2 + this->T3;

	this->C1 = (this->Sm - this->Si) / this->T1; // Departure phase slope
	this->C3 = (this->Sf - this->Sm) / this->T3; // Arrival phase slope
}

float SpeedPositionPlanner::planned_total_time()
{
	return this->T;
}

float SpeedPositionPlanner::planned_speed(float t)
{
	if (t > this->planned_total_time())
	{
		return this->Sf;
	}
	else
	{
		float V1 = this->Si + this->C1 * t;
		float V2 = this->Sm;
		float V3 = this->Sf + this->C3 * (t - this->T);

		return std::min(std::min(V1, V2), V3);
	}
}

float SpeedPositionPlanner::planned_position(float t)
{
	// Phase 1: Departure
	if (t <= this->T1)
	{
		return this->Si * t + 0.5 * this->C1 * t * t;
	}
	// Phase 2: Max speed
	else if (t <= this->T1 + this->T2)
	{
		float t_m = t - this->T1;
		return this->D1 + this->Sm * t_m;
	}
	// Phase 3: Arrival
	else if (t <= this->T)
	{
		float t_a = t - this->T1 - this->T2;
		return this->D1 + this->D2 + this->Sm * t_a + 0.5 * this->C3 * t_a * t_a;
	}
	// After planned time, position remains at final distance D
	else
	{
		return this->D;
	}
}
	