#include <Arduino.h>
#include <TimerOne.h>
#include <rolling_basis.h>
#include <util/atomic.h>
#include <messages.h>

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
#define Kp 1.5
#define Ki 0.0
#define Kd 0.0

#define RIGHT_MOTOR_POWER_FACTOR 1.0
#define LEFT_MOTOR_POWER_FACTOR 1.17

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
    TRAJECTORY_PRECISION,
};

Rolling_Basis_Ptrs rolling_basis_ptrs;

/* Strat part */
Com *com;
// template <typename T>
// T decode(byte *data, size_t size)
// {
//   T value;
//   memcpy(&value, data, size);
//   return value;
// }

// template <typename T>
// void encode(byte *data, T value, size_t size)
// {
//   memcpy(data, &value, size);
// }

Complex_Action *current_action = nullptr;

void swap_action(Complex_Action *new_action)
{
  // implémentation des destructeurs manquante
  if (current_action != nullptr)
    free(current_action);
  current_action = new_action;
}

void go_to(byte *msg, byte size)
{
  msg_Go_To *go_to_msg = (msg_Go_To *)msg;
  Point target_point(go_to_msg->x, go_to_msg->y, 0.0f);

  Precision_Params params{
      go_to_msg->next_position_delay,
      go_to_msg->action_error_auth,
      go_to_msg->traj_precision,
  };

  Go_To *new_action = new Go_To(target_point, go_to_msg->is_forward ? backward : forward, go_to_msg->speed, params);
  if (current_action == new_action)
    free(new_action);
  else
    swap_action(new_action);
}

void curve_go_to(byte *msg, byte size)
{
  // float target_x = (float)(msg[0]);
  // float target_y = (float)(msg[sizeof(float)]);

  // float center_x = (float)(msg[2 * sizeof(float)]);
  // float center_y = (float)(msg[3 * sizeof(float)]);

  // unsigned short interval = (unsigned short)(msg[4 * sizeof(float)]);

  // Point target_point = Point(target_x, target_y);
  // Point center_point = Point(center_x, center_y);

  // bool is_identical = current_action->get_id() == CURVE_GO_TO;
  // if (is_identical)
  // {
  //   Go_To *casted_action = ;
  //   is_identical = ((Go_To *)current_action)->target_point == target_point;
  // }
}

// Whether to keep position when no action is active
bool keep_curr_pos_when_no_action = false;

void keep_current_position(byte *msg, byte size)
{
  free(current_action);
  current_action = nullptr;
  // last_ticks_position = rolling_basis_ptr->get_current_ticks();

  keep_curr_pos_when_no_action = true;

  msg_Action_Finished fin_msg;
  fin_msg.action_id = KEEP_CURRENT_POSITION;
  com->send_msg((byte *)&fin_msg, sizeof(msg_Action_Finished));
}

void disable_pid(byte *msg, byte size)
{
  keep_curr_pos_when_no_action = false;

  msg_Action_Finished fin_msg;
  fin_msg.action_id = DISABLE_PID;
  com->send_msg((byte *)&fin_msg, sizeof(msg_Action_Finished));
}

void enable_pid(byte *msg, byte size)
{
  // last_ticks_position = rolling_basis_ptr->get_current_ticks();
  keep_curr_pos_when_no_action = true;

  msg_Action_Finished fin_msg;
  fin_msg.action_id = ENABLE_PID;
  com->send_msg((byte *)&fin_msg, sizeof(msg_Action_Finished));
}

void reset_position(byte *msg, byte size)
{
  rolling_basis_ptr->reset_position();

  msg_Action_Finished fin_msg;
  fin_msg.action_id = RESET_POSITION;
  com->send_msg((byte *)&fin_msg, sizeof(msg_Action_Finished));
}

void stop(byte *msg, byte size)
{
  free(current_action);
  current_action = nullptr;

  rolling_basis_ptr->shutdown_motor();

  msg_Action_Finished fin_msg;
  fin_msg.action_id = STOP;
  com->send_msg((byte *)&fin_msg, sizeof(msg_Action_Finished));
}

void (*functions[256])(byte *msg, byte size);

extern void handle_callback(Com *com);

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

// Pin ON / OFF
byte pin_on_off = 19;

// Switch side
byte pin_green_side = 18;

// Globales variables
Ticks last_ticks_position;

long start_time = -1;

void handle();

void setup()
{
  com = new Com(&Serial, 115200);

  // only the messages received by the teensy are listed here
  functions[GO_TO] = &go_to,
  functions[CURVE_GO_TO] = &curve_go_to,
  functions[KEEP_CURRENT_POSITION] = &keep_current_position,
  functions[DISABLE_PID] = &disable_pid,
  functions[ENABLE_PID] = &enable_pid,
  functions[RESET_POSITION] = &reset_position,
  functions[STOP] = &stop;

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

int counter = 0;
int cooldown = 0;

void loop()
{
  rolling_basis_ptr->odometrie_handle();
  rolling_basis_ptr->is_running_update();

  if (start_time == -1)
    start_time = millis();

  // Com
  handle_callback(com);

  // Send odometrie
  msg_Update_Position pos_msg;
  if (counter++ > 1024)
  {
    pos_msg.x = rolling_basis_ptr->X;
    pos_msg.y = rolling_basis_ptr->Y;
    pos_msg.theta = rolling_basis_ptr->THETA;
    com->send_msg((byte *)&pos_msg, sizeof(msg_Update_Position));
    counter = 0;
  }
}

void handle()
{
  if (current_action == nullptr || current_action->is_finished())
  {
    if (keep_curr_pos_when_no_action)
      rolling_basis_ptr->keep_position(last_ticks_position.right, last_ticks_position.left);
    return;
  }

  Point current_position = rolling_basis_ptr->get_current_position();
  last_ticks_position = rolling_basis_ptr->get_current_ticks();

  current_action->handle(
      current_position,
      last_ticks_position,
      &rolling_basis_ptrs);

  if (current_action->is_finished())
  {
    msg_Action_Finished fin_msg;
    fin_msg.action_id = current_action->get_id();
    com->send_msg((byte *)&fin_msg, sizeof(msg_Action_Finished));
  }
  return;
}

/*

 This code was realized by Florian BARRE
    ____ __
   / __// /___<
  / _/ / // _ \
 /_/  /_/ \___/

*/
