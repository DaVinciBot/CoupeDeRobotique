#pragma once

// Use the lightweight fake Arduino header when running native unit tests.
#ifdef UNIT_TEST
#include "Arduino.h"
#else
#include <Arduino.h>
#endif
