#include <Arduino.h>
#include <com.h>

#define GO_TO 0
#define CURVE_GO_TO 1

extern void (*functions[256])(byte *msg, byte size);
extern void handle_callback(Com *com);