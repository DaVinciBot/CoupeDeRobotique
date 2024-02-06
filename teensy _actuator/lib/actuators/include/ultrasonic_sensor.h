#include <Ultrasonic.h>
struct Ultrasonic_Sensor
{
    Ultrasonic* actuator;
    int trigger_pin;
    int echo_pin;
};