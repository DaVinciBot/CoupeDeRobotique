// #include "com.h"
#include "config.h"

Motor leftMotor(LEFT_STEP_PIN, LEFT_DIR_PIN, LEFT_EN_PIN, 400);
Motor rightMotor(RIGHT_STEP_PIN, RIGHT_DIR_PIN, RIGHT_EN_PIN, 400);

#if ENABLE_OTA
#include "OTA.h"
AsyncWebServer server(80);
CustomOTA ota("DVB", "davincibot", &server);
#endif

// Com *com = new Com(); // LoRa object

void print_debug(byte *msg, byte size)
{
    Serial.print("Received message: ");
    for (int i = 0; i < size; i++)
    {
        Serial.print(msg[i], HEX);
        Serial.print(" ");
    }
    Serial.println();
}

void (*callback_functions[256])(byte *msg, byte size);

void initialize_callback_functions()
{
    // callback_functions[SET_POSITION] = &set_speed_and_position;
    // callback_functions[SET_PID] = &set_pid;
    // callback_functions[SET_ODOMETRIE] = &set_odometrie;
    //   callback_functions[RESET_PAMI] = &reset_teensy;
    // callback_functions[PRINT] = &print_debug;
}
void setup()
{
    Serial.begin(115200);
    Serial.println("\n-- PAMI test --\n");
    // com->begin(SS, RST, BUSY, IRQ, TXEN, RXEN); // NSS, RESET, BUSY, IRQ, TXEN, RXEN pins
    leftMotor.init();
    leftMotor.enableMotor(true);
    leftMotor.setAcceleration(100.0f);

    rightMotor.init();
    rightMotor.enableMotor(true);
    rightMotor.setAcceleration(100.0f);

    Serial.println("Motors initialized");

#if ENABLE_OTA
    ota.begin();
    server.begin();
#endif

    initialize_callback_functions();
}
int counter = 0;
int current_speed = 0;
bool decreasing = false;

void loop()
{
    rightMotor.update();
    leftMotor.update();

    if (counter++ > 15024)
    {        
        counter = 0;
        current_speed += decreasing ? -10 : 10;
        if (current_speed >= 1000)
        {
            decreasing = true;
        }
        else if (current_speed <= 0)
        {
            decreasing = false;
        }
        leftMotor.setTargetSpeed(current_speed);
        rightMotor.setTargetSpeed(current_speed);
        Serial.print("Current speed: ");
        Serial.println(current_speed);

    }
#if ENABLE_OTA
    ota.loop();
#endif
}
