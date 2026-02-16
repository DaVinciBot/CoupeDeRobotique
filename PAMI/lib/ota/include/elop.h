#ifndef elop_h
#define elop_h

#include <Arduino.h>

// Declaration without fixed size avoids mismatch when the generated
// HTML array length changes. Keep PROGMEM so the symbol is placed in
// flash (same storage qualifier as the definition in elop.cpp).
extern const uint8_t ELEGANT_HTML[] PROGMEM;
// Length exported so other translation units can use it without
// applying sizeof() to an incomplete extern array.
extern const size_t ELEGANT_HTML_LEN;
// previous explicit sizes (kept for reference):
// extern const uint8_t ELEGANT_HTML[11656];
// extern const uint8_t ELEGANT_HTML[10273]; with old logo

#endif
