#include <Arduino.h>
#include <com.h>

#define GO_TO 0
#define CURVE_GO_TO 1
#define KEEP_CURRENT_POSITION 2
#define DISABLE_PID 3
#define ENABLE_PID 4

#define UPDATE_POSITION 128
#define ACTION_FINISHED 129

extern void (*functions[256])(byte *msg, byte size);
extern void handle_callback(Com *com);