#include <iostream>
#include <cmath>

// This class is used to generate a speed curve for a movement (used for robot trajectory planning)
class SpeedPositionPlanner
{
private:
    // Initial, max and final speeds (given by constructor)
	float Si, Sm, Sf;
	// Tota, acceleration, max speed and deceleration distances (given by constructor)
	float D, D1, D2, D3; 
	// Total, acceleration, max speed and deceleration times (calculated)
	float T, T1, T2, T3;
	// Slopes of acceleration and deceleration phases (calculated)
	float C1, C3;

public:
	SpeedPositionPlanner(
		float max_speed, 
		float total_distance, 
		float acceleration_distance, float deceleration_distance,
		float intial_speed = 0.0f, float final_speed = 0.0f
	);
	~SpeedPositionPlanner() = default;

	float planned_speed(float t);
	float planned_position(float t);
	float planned_total_time();
};
