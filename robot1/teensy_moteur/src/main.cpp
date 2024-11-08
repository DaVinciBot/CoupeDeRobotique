#include <Arduino.h>
#include <TimerOne.h>
#include <rolling_basis.h>
#include <util/atomic.h>
#include <speed_and_position_planner.h>

// PID
#define MAX_PWM 160
#define L_Kp 10.0
#define L_Ki 0.0
#define L_Kd 0.0

#define R_Kp 10.0
#define R_Ki 0.0
#define R_Kd 0.0

// Default position
#define START_X 0.0
#define START_Y 0.0
#define START_THETA 0.0

// Motor Left
#define L_ENCA 12
#define L_ENCB 11
#define L_PWM 5
#define L_IN2 3
#define L_IN1 4

// Motor Right
#define R_ENCA 14 // Va te faire foutre (Flo)
#define R_ENCB 13 // Si rien ne marche change les pins
#define R_PWM 2
#define R_IN2 1
#define R_IN1 0

// Creation Rolling Basis
// New encoder
#define ENCODER_RESOLUTION 600
#define CENTER_DISTANCE 33.57
#define WHEEL_DIAMETER 6.1

PID linear_speed_pid(0, 0, 0);
PID angular_speed_pid(0, 0, 0);

PID linear_distance_pid(10, 0, 0);
PID angular_distance_pid(0, 0, 0);


Rolling_Basis *rolling_basis_ptr = new Rolling_Basis(
  ENCODER_RESOLUTION, CENTER_DISTANCE, WHEEL_DIAMETER,
  linear_speed_pid, angular_speed_pid, linear_distance_pid, angular_distance_pid
);


/******* Attach Interrupt *******/
inline void left_motor_read_encoder()
{
  if (digitalRead(L_ENCB))
      rolling_basis_ptr->left_motor->ticks--;
  else
      rolling_basis_ptr->left_motor->ticks++;
}

inline void right_motor_read_encoder()
{
  if (digitalRead(R_ENCB))
      rolling_basis_ptr->right_motor->ticks--;
  else
      rolling_basis_ptr->right_motor->ticks++;
}


void handle();


SpeedPositionPlanner *path = new SpeedPositionPlanner(50, 80, 5, 5);
long start_time = 0;

void setup()
{
  Serial.begin(115200);

  // Change pwm frequency
  analogWriteFrequency(R_PWM, 40000);
  analogWriteFrequency(L_PWM, 40000);

  // Init Rolling Basis
  rolling_basis_ptr->define_right_motor(R_ENCA, R_ENCB, R_PWM, R_IN2, R_IN1, MAX_PWM);
  rolling_basis_ptr->define_left_motor( L_ENCA, L_ENCB, L_PWM, L_IN2, L_IN1, MAX_PWM);
  rolling_basis_ptr->init_motors();

  rolling_basis_ptr->init_rolling_basis(START_X, START_Y, START_THETA);
  attachInterrupt(digitalPinToInterrupt(L_ENCA), left_motor_read_encoder, RISING);
  attachInterrupt(digitalPinToInterrupt(R_ENCA), right_motor_read_encoder, RISING);

  // Init motors handle timer
  Timer1.initialize(10000);
  Timer1.attachInterrupt(handle);

  start_time = millis();
}

void loop()
{

}

bool millis_to_bool(int half_period_duration, float offset = 1.0f){
  return millis() % (half_period_duration * 2) < half_period_duration * offset;
}


void handle()
{
  rolling_basis_ptr->odometrie_handle();
  float elapsed_time = (millis() - start_time) / 1000.0;
  float planned_speed = path->planned_speed(elapsed_time);
  float planned_x = path->planned_position(elapsed_time);
  Point planned_point(planned_x, 0, 0);

  Serial.println(String("Elapsed time: ") + String(elapsed_time) + String(" | Planned speed: ") + String(planned_speed) + String(" | Planned position: ") + String(planned_x));
  
  rolling_basis_ptr->handle(planned_point, planned_speed, 0.0);
}

/*

 This code was realized by Florian BARRE
    ____ __
   / __// /___
  / _/ / // _ \
 /_/  /_/ \___/

*/
