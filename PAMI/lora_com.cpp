#include "lora_com.h"
#include <Arduino.h>
#include <RadioLib.h>
#include <modules/SX126x/patches/SX126x_patch_scan.h>


lora_com loraController;

void setup() {
  Serial.begin(115200);
  delay(5000);
  loraController.begin();
}

void loop() {
  loraController.update();
}
lora_com::lora_com()
{

}

lora_com::~lora_com()
{

}
