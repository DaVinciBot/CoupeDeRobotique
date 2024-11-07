#include <Arduino.h>
#include <com.h>

// rasp -> teensy : 0-127 (Convention)
#define GO_TO 0
#define CURVE_GO_TO 1
#define KEEP_CURRENT_POSITION 2
#define DISABLE_PIDS 3
#define ENABLE_PIDS 4
#define RESET_ODO 5
#define SET_PIDS 6
#define SET_HOME 7
#define GET_ORIENTATION 8
#define GET_PID 9

// two ways : 127 (Convention)
#define NACK 127

// teensy -> rasp : 128-255 (Convention)
#define UPDATE_POSITION 128
#define ACTION_FINISHED 129
#define STRING 130
#define SEND_PID 131
#define UNKNOWN_MSG_TYPE 255

extern void (*functions[256])(byte *msg, byte size);
extern void handle_callback(Com *com);

struct msg_Unknown_Msg_Type
{
    byte command = UNKNOWN_MSG_TYPE;
    byte type_id;
};