#include <Arduino.h>
#include <TimerOne.h>
#include <rolling_basis.h>
#include <util/atomic.h>

// Mouvement params
#define ACTION_ERROR_AUTH 20
#define TRAJECTORY_PRECISION 50
#define NEXT_POSITION_DELAY 100
#define INACTIVE_DELAY 2000
#define RETURN_START_POSITION_DELAY 999999
#define STOP_MOTORS_DELAY 999999
#define DISTANCE_NEAR_START_POSITION 30.0

// PID
#define MAX_PWM 150
#define LOW_PWM 80 // To use for pecise action with low speed
#define Kp 7.5
#define Ki 0.0
#define Kd 1.0

#define RIGHT_MOTOR_POWER_FACTOR 1.0
#define LEFT_MOTOR_POWER_FACTOR 1.0

// Default position
#define START_X 0.0
#define START_Y 0.0
#define START_THETA 0.0

// Creation Rolling Basis
#define ENCODER_RESOLUTION 1024
#define CENTER_DISTANCE 27.07
#define WHEEL_DIAMETER 6.1

// Motor Left
#define L_ENCA 12
#define L_ENCB 11
#define L_PWM 5
#define L_IN2 3
#define L_IN1 4

// Motor Right
#define R_ENCA 14
#define R_ENCB 13
#define R_PWM 2
#define R_IN2 1
#define R_IN1 0

Rolling_Basis *rolling_basis_ptr = new Rolling_Basis(ENCODER_RESOLUTION, CENTER_DISTANCE, WHEEL_DIAMETER);

Rolling_Basis_Params rolling_basis_params{
    rolling_basis_ptr->encoder_resolution,
    rolling_basis_ptr->wheel_perimeter(),
    rolling_basis_ptr->radius(),
};

Precision_Params classic_params{
    NEXT_POSITION_DELAY,
    ACTION_ERROR_AUTH,
    TRAJECTORY_PRECISION
};

Rolling_Basis_Ptrs rolling_basis_ptrs;

/* Strat part */
#define STRAT_SIZE 3
byte action_index = 0;

Profil_params a = {80, -1.0f, 100.0};
Profil_params d = {80, -1.0f, 100.0};

Action **strat_test = new Action *[STRAT_SIZE]
{
  new Go_To(Point(150.0, 0.0),  forward, Speed_Driver_From_Distance(150, a, d), classic_params), 
  //new Go_To(Point(100.0, 50.0), forward, Speed_Driver_From_Distance(150, a, d), classic_params), 
  //new Go_To(Point(0.0, 50.0),   forward, Speed_Driver_From_Distance(150, a, d), classic_params), 
  //new Go_To(Point(30.0, 0.0), backward, Speed_Driver_From_Distance(100, 50, 5.0), classic_params),
  //new Go_To(Point(0.0, 0.0), backward, Speed_Driver_From_Distance(100, 50, 10.0), classic_params),
  //new Curve_Go_To(Point(100.0, 0.0), Point(50.0, 0.0), 5, forward, Speed_Driver_From_Distance(100, 50, 0.1), classic_params),
};

/******* Attach Interrupt *******/
inline void left_motor_read_encoder()
{
  if (digitalReadFast(L_ENCB) > 0)
    rolling_basis_ptr->left_motor->ticks++;
  else
    rolling_basis_ptr->left_motor->ticks--;
}

inline void right_motor_read_encoder()
{
  if (digitalReadFast(R_ENCB) > 0)
    rolling_basis_ptr->right_motor->ticks++;
  else
    rolling_basis_ptr->right_motor->ticks--;
}

// Globales variables 
Ticks last_ticks_position;

long start_time = -1;

void handle();

void setup()
{
  Serial.begin(115200);

  // Change pwm frequency
  analogWriteFrequency(R_PWM, 40000);
  analogWriteFrequency(L_PWM, 40000);

  // Init motors
  rolling_basis_ptr->init_right_motor(R_IN1, R_IN2, R_PWM, R_ENCA, R_ENCB, Kp, Ki, Kd, RIGHT_MOTOR_POWER_FACTOR, 0);
  rolling_basis_ptr->init_left_motor(L_IN1, L_IN2, L_PWM, L_ENCA, L_ENCB, Kp, Ki, Kd, LEFT_MOTOR_POWER_FACTOR, 0);
  rolling_basis_ptr->init_motors();

  rolling_basis_ptrs = {
      &rolling_basis_params,
      rolling_basis_ptr->right_motor,
      rolling_basis_ptr->left_motor,
  };

  // Init Rolling Basis
  rolling_basis_ptr->init_rolling_basis(START_X, START_Y, START_THETA, INACTIVE_DELAY, MAX_PWM);
  attachInterrupt(digitalPinToInterrupt(L_ENCA), left_motor_read_encoder, RISING);
  attachInterrupt(digitalPinToInterrupt(R_ENCA), right_motor_read_encoder, RISING);

  // Init motors handle timer
  Timer1.initialize(10000);
  Timer1.attachInterrupt(handle);
}

void loop()
{
  rolling_basis_ptr->odometrie_handle();
  rolling_basis_ptr->is_running_update();
}

void handle(){
    // Do classic trajectory
    if (action_index < STRAT_SIZE)
    {
      Point current_position = rolling_basis_ptr->get_current_position();
      last_ticks_position = rolling_basis_ptr->get_current_ticks();

      if (!strat_test[action_index]->is_finished())
        strat_test[action_index]->handle(
            current_position,
            last_ticks_position,
            &rolling_basis_ptrs);
      else
        action_index++;
    }
    else
      rolling_basis_ptr->keep_position(last_ticks_position.right, last_ticks_position.left);

}

// This code was realized by Florian BARRE
//     ____ __
//    / __// /___
//   / _/ / // _ \
//  /_/  /_/ \___/


