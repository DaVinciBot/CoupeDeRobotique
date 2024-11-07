#include "com.h"

// Create global variables
bool enable_to_start = false;

// Instantiate com
Com com(
    "DVB_CDR",
    "ROAD_T0_TOP1",

    "rc.local",
    8080,
    "/pami",

    "pami" // Have to be unique, can't use th same username for multiple PAMI
);

// Com callbacks
void update_start(String data){
  // If the data value is different to 0, turn enable_to_start to true
  enable_to_start = (data.toInt() != 0);
}

void setup() {
  com.begin();
  com.add_callback("tirette", update_start);

  // An exemple to send message to the server through websocket 
  com.send("connected", "hello, i am a esp32 c3");
}

void loop() {
  com.handle();
}