#include <Arduino.h>
#include <TimerOne.h>
#include <rolling_basis.h>
#include <util/atomic.h>
#include <messages.h>

#define INACTIVE_DELAY 4000

// PID
#define MAX_PWM 200
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

Rolling_Basis_Ptrs rolling_basis_ptrs;

/* Strat part */
Com *com;

Complex_Action *current_action = nullptr;
Complex_Action *next_action = nullptr;

bool keep_curr_pos_when_no_action = true;

void swap_action(Complex_Action *new_action, bool is_preshot = false)
{
  // implémentation des destructeurs manquante
  if (current_action == new_action)
  {
    free(new_action);
    return;
  }
  if (current_action != nullptr)
    free(current_action);
  if (is_preshot)
  {
    next_action = new_action;
  }
  else
  {
    current_action = new_action;
  }
}

void go_to(byte *msg, byte size, bool is_preshot = false)
{
  msg_Go_To *go_to_msg = (msg_Go_To *)msg;
  Point target_point(go_to_msg->x, go_to_msg->y, 0.0f);

  Precision_Params params{
      go_to_msg->next_position_delay,
      go_to_msg->action_error_auth,
      go_to_msg->traj_precision,
  };

  Profil_params acceleration{
      go_to_msg->acceleration_start_speed,
      -1.0f,
      go_to_msg->acceleration_distance};

  Profil_params deceleration{
      go_to_msg->deceleration_end_speed,
      -1.0f,
      go_to_msg->deceleration_distance};

  Go_To *new_action = new Go_To(
      target_point,
      go_to_msg->is_forward ? forward : backward,
      Speed_Driver_From_Distance(
          go_to_msg->max_speed,
          go_to_msg->correction_trajectory_speed,
          acceleration,
          deceleration),
      params);

  swap_action(new_action, is_preshot);
}
/*
void curve_go_to(byte *msg, byte size, bool is_preshot = false)
{
  msg_Curve_Go_To *curve_msg = (msg_Curve_Go_To *)msg;

  Point target_point = Point(curve_msg->target_x, curve_msg->target_y, 0.0f);
  Point center_point = Point(curve_msg->center_x, curve_msg->center_y, 0.0f);

  Precision_Params params{
      curve_msg->next_position_delay,
      curve_msg->action_error_auth,
      curve_msg->traj_precision,
  };

  Curve_Go_To *new_action = new Curve_Go_To(target_point, center_point, curve_msg->interval, curve_msg->direction ? backward : forward, curve_msg->speed, params);
  swap_action(new_action);
}*/

// Whether to keep position when no action is active

void keep_current_position(byte *msg, byte size, bool is_preshot = false)
{
  free(current_action);
  current_action = nullptr;
  // last_ticks_position = rolling_basis_ptr->get_current_ticks();

  keep_curr_pos_when_no_action = true;

  msg_Action_Finished fin_msg;
  fin_msg.action_id = KEEP_CURRENT_POSITION;
  com->send_msg((byte *)&fin_msg, sizeof(msg_Action_Finished));
}

void disable_pid(byte *msg, byte size, bool is_preshot = false)
{
  keep_curr_pos_when_no_action = false;

  msg_Action_Finished fin_msg;
  fin_msg.action_id = DISABLE_PID;
  com->send_msg((byte *)&fin_msg, sizeof(msg_Action_Finished));
}

void enable_pid(byte *msg, byte size, bool is_preshot = false)
{
  // last_ticks_position = rolling_basis_ptr->get_current_ticks();
  keep_curr_pos_when_no_action = true;

  msg_Action_Finished fin_msg;
  fin_msg.action_id = ENABLE_PID;
  com->send_msg((byte *)&fin_msg, sizeof(msg_Action_Finished));
}

void reset_odo(byte *msg, byte size, bool is_preshot = false)
{
  rolling_basis_ptr->reset_position();

  msg_Action_Finished fin_msg;
  fin_msg.action_id = RESET_ODO;
  com->send_msg((byte *)&fin_msg, sizeof(msg_Action_Finished));
}

void set_pid(byte *msg, byte size, bool is_preshot = false)
{
  msg_Set_PID *pid_msg = (msg_Set_PID *)msg;
  // Update motors PID
  rolling_basis_ptr->right_motor->kp = pid_msg->kp;
  rolling_basis_ptr->right_motor->ki = pid_msg->ki;
  rolling_basis_ptr->right_motor->kd = pid_msg->kd;

  rolling_basis_ptr->left_motor->kp = pid_msg->kp;
  rolling_basis_ptr->left_motor->ki = pid_msg->ki;
  rolling_basis_ptr->left_motor->kd = pid_msg->kd;

  msg_Action_Finished fin_msg;
  fin_msg.action_id = SET_PID;
  com->send_msg((byte *)&fin_msg, sizeof(msg_Action_Finished));
}

void set_home(byte *msg, byte size, bool is_preshot = false)
{
  msg_Set_Home *home_msg = (msg_Set_Home *)msg;
  rolling_basis_ptr->X = home_msg->x;
  rolling_basis_ptr->Y = home_msg->y;
  rolling_basis_ptr->THETA = home_msg->theta;

  msg_Action_Finished fin_msg;
  fin_msg.action_id = SET_HOME;
  com->send_msg((byte *)&fin_msg, sizeof(msg_Action_Finished));
}



void (*functions[256])(byte *msg, byte size, bool is_preshot);

void preshot(byte *msg, byte size, bool is_preshot = false)
{
  // get the second byte to get the data type
  msg_Preshot *preshot_msg = (msg_Preshot *)msg;
  byte msg_type = preshot_msg->msg_type;

  //create a blob with data type + data
  byte data[250];
  data[0] = msg_type;
  for (int i = 0; i < 249; i++)
  {
    data[i+1] = preshot_msg->data[i];
  }
  functions[msg_type](data, 250, true);
}

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

// Globales variables
Ticks last_ticks_position;

long start_time = -1;

void handle();

void setup()
{
  com = new Com(&Serial, 115200);

  // only the messages received by the teensy are listed here
  functions[GO_TO] = &go_to,
  //functions[CURVE_GO_TO] = &curve_go_to,
  functions[KEEP_CURRENT_POSITION] = &keep_current_position,
  functions[DISABLE_PID] = &disable_pid,
  functions[ENABLE_PID] = &enable_pid,
  functions[RESET_ODO] = &reset_odo,
  functions[SET_PID] = &set_pid,
  functions[SET_HOME] = &set_home,
  functions[PRESHOT] = &preshot,

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
    {
      rolling_basis_ptr->keep_position(last_ticks_position.right, last_ticks_position.left);
    }
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
    swap_action(next_action);
  }
}

/*

 This code was realized by Florian BARRE
    ____ __
   / __// /___
  / _/ / // _ \
 /_/  /_/ \___/

*/
