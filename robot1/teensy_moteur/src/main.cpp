// Externe libraries used: Arduino, TimerOne, ATOMIC
#include <Arduino.h>     // Arduino framework
#include <TimerOne.h>    // Timer interrupt library
#include <util/atomic.h> // Atomic block library

// Custom libraries used: RollingBasis, Com
#include <rolling_basis.h> // Rolling Basis object to manage the motors and robot position
#include <com.h>           // Communication object to manage the communication between the teensy and the Raspberry Pi

// Configuration file (contains all the constants and pinout), it is just a main.cpp header file
#include <config.h>

// tmp
#include <speed_and_position_planner.h>
// tmp

// 1. Instanciate the Rolling Basis object
// a. Define the PID controllers
PID linear_speed_pid(KP_LINEAR_SPEED, KI_LINEAR_SPEED, KD_LINEAR_SPEED);
PID angular_speed_pid(KP_ANGULAR_SPEED, KI_ANGULAR_SPEED, KD_ANGULAR_SPEED);

PID linear_distance_pid(KP_LINEAR_DISTANCE, KI_LINEAR_DISTANCE, KD_LINEAR_DISTANCE);  
PID angular_distance_pid(KP_ANGULAR_DISTANCE, KI_ANGULAR_DISTANCE, KD_ANGULAR_DISTANCE);  

// b. Instanciate the Rolling Basis object
Rolling_Basis *rolling_basis_ptr = new Rolling_Basis(
  ENCODER_RESOLUTION, CENTER_DISTANCE, WHEEL_DIAMETER,
  linear_speed_pid, angular_speed_pid, linear_distance_pid, angular_distance_pid
);

// c. Define the motors interrupt functions
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

// 2. Instanciate the Communication object
Com *com;

// 3. Define all com callback functions
// a. define globals variables to keep in memory callback functions updated
Point target_position(START_X, START_Y, START_THETA);
float target_linear_speed  = 0.0f;
float target_angular_speed = 0.0f;

// b. define the callback functions
void set_speed_and_position(byte *msg, byte size)
{
  msg_set_speed_and_position *target_speed_and_position = (msg_set_speed_and_position *)msg;

  // Update speeds
  target_linear_speed = target_speed_and_position->target_linear_speed;
  target_angular_speed = target_speed_and_position->target_angular_speed;

  // Update position
  target_position.x = target_speed_and_position->target_position_x;
  target_position.y = target_speed_and_position->target_position_y;
  target_position.theta = target_speed_and_position->target_position_theta;
}

// c. assign the callback functions to the right message id
void (*callback_functions[256])(byte *msg, byte size);

void initialize_callback_functions() {
  callback_functions[SET_SPEED_AND_POSITION] = &set_speed_and_position;
}

// Tmp
SpeedPositionPlanner *path = new SpeedPositionPlanner(100, 250, 10, 10, 0.0f, 0.0f);
long start_time = 0;

bool millis_to_bool(int half_period_duration, float offset = 1.0f){
  return millis() % (half_period_duration * 2) < half_period_duration * offset;
}

// Tmp


// 4. Define the timer interrupt handle function (this function will be called every 10ms, and which manage the robot position and speed: asservissement)
void handle()
{
  // rolling_basis_ptr->odometrie_handle();
  // float elapsed_time = (millis() - start_time) / 1000.0;
  // float planned_speed = path->planned_speed(elapsed_time);
  // float planned_x = path->planned_position(elapsed_time);
  // Point planned_point(planned_x, 0, 0);

  // //Serial.println(String("Elapsed time: ") + String(elapsed_time) + String(" | Planned speed: ") + String(planned_speed) + String(" | Planned position: ") + String(planned_x));
  
  // rolling_basis_ptr->handle(planned_point, planned_speed, 0.0);

  rolling_basis_ptr->odometrie_handle();
  rolling_basis_ptr->handle(target_position, target_linear_speed, target_angular_speed);
}



void setup()
{
  com = new Com(&Serial, BAUDRATE);

  // Change pwm frequency
  analogWriteFrequency(R_PWM, PWM_FREQUENCY);
  analogWriteFrequency(L_PWM, PWM_FREQUENCY);

  // Init Rolling Basis
  rolling_basis_ptr->define_right_motor(R_ENCA, R_ENCB, R_PWM, R_IN2, R_IN1, MAX_PWM);
  rolling_basis_ptr->define_left_motor( L_ENCA, L_ENCB, L_PWM, L_IN2, L_IN1, MAX_PWM);
  rolling_basis_ptr->init_motors();

  rolling_basis_ptr->init_rolling_basis(START_X, START_Y, START_THETA);
  attachInterrupt(digitalPinToInterrupt(L_ENCA), left_motor_read_encoder, RISING);
  attachInterrupt(digitalPinToInterrupt(R_ENCA), right_motor_read_encoder, RISING);

  // Init motors handle timer
  Timer1.initialize(ASSERVISSEMENT_FREQUENCY);
  Timer1.attachInterrupt(handle);

  // Initializa callback functions
  initialize_callback_functions();

  start_time = millis();
}


uint_fast32_t counter = 0;
void loop()
{
  // Handle the communication 
  com->handle();
  
  // Send rolling basis state
  msg_update_rolling_basis rolling_basis_msg;
  if (counter++ > 1024)
  {
    // Rolling Basis position
    rolling_basis_msg.x = rolling_basis_ptr->X;
    rolling_basis_msg.y = rolling_basis_ptr->Y;
    rolling_basis_msg.theta = rolling_basis_ptr->THETA;
    // Rolling Basis speeds
    rolling_basis_msg.current_linear_speed = rolling_basis_ptr->linear_speed;
    rolling_basis_msg.current_angular_speed = rolling_basis_ptr->angular_speed;

    com->send_msg((byte *)&rolling_basis_msg, sizeof(msg_update_rolling_basis));
    counter = 0;
  }
}

/*

 This code was realized by Florian BARRE
    ____ __
   / __// /___
  / _/ / // _ \
 /_/  /_/ \___/

*/
