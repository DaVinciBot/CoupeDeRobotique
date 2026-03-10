#pragma once

// Use the lightweight fake Arduino header when running native unit tests.
#ifdef UNIT_TEST
#include "Arduino.h"
#else
#include <Arduino.h>
#endif

// Provide math constants when the toolchain doesn't define them (e.g., MSVC).
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif
