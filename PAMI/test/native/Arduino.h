#pragma once

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <string>

using byte = uint8_t;
using std::max;

class FakeSerial {
   public:
    void begin(unsigned long) {}
    void println(const char*) {}
    void println(float) {}
    void println(int) {}
    void println(unsigned long) {}
    void print(const char*) {}
    void print(int) {}
    void print(float) {}
    void printf(const char*, ...) {}
};

inline FakeSerial Serial;
inline FakeSerial Serial0;

inline unsigned long _fakeMicros = 0;

inline void resetFakeTime(unsigned long us = 0) { _fakeMicros = us; }
inline void advanceFakeMicros(unsigned long deltaUs) { _fakeMicros += deltaUs; }
inline unsigned long micros() { return _fakeMicros; }
inline unsigned long millis() { return _fakeMicros / 1000; }
inline void delayMicroseconds(unsigned int us) { _fakeMicros += us; }
inline void delay(unsigned long ms) { _fakeMicros += ms * 1000; }

inline void pinMode(int, int) {}
inline void digitalWrite(int, int) {}
inline void setCpuFrequencyMhz(int) {}

inline long random(long maxVal) { return std::rand() % maxVal; }
inline long random(long minVal, long maxVal) {
    return minVal + (std::rand() % (maxVal - minVal));
}

#define OUTPUT 0x1
#define INPUT 0x0
#define HIGH 0x1
#define LOW 0x0

#ifndef PI
#define PI 3.14159265358979323846
#endif
