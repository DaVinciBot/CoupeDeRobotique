#include "com.h"
#include "config.h"

Motor leftMotor(LEFT_STEP_PIN, LEFT_DIR_PIN, LEFT_EN_PIN, LEFT_STEPS_PER_REV);
Motor rightMotor(RIGHT_STEP_PIN, RIGHT_DIR_PIN, RIGHT_EN_PIN, RIGHT_STEPS_PER_REV);

#if ENABLE_OTA
#include "OTA.h"
AsyncWebServer server(80);
CustomOTA ota("DVB", "davincibot", &server);
#endif

Com *com = new Com(); // LoRa object

void print_debug(byte *msg, byte size)
{
    msg_print *message = (msg_print *)msg;
    Serial.print("Received message: ");
    Serial.println((char *)(message->message));
}
void deffault_func(byte *msg, byte size)
{
    Serial.print("null");
}
// void set_speed(byte *msg, byte size)
// {
//     msg_set_speed *message = (msg_set_speed *)msg;

//     leftMotor.setTargetSpeed(message->speed);
//     rightMotor.setTargetSpeed(message->speed);

//     Serial.print("Set speed: ");
//     Serial.println(message->speed);
// }

void (*callback_functions[256])(byte *msg, byte size);

void initialize_callback_functions()
{
    // callback_functions[SET_SPEED] = &set_speed;
    // callback_functions[SET_PID] = &set_pid;
    // callback_functions[SET_ODOMETRIE] = &set_odometrie;
    // callback_functions[RESET_PAMI] = &reset_pami;
    callback_functions[PRINT] = &print_debug;
    //bind the rest to the default function
    for (int i = 0; i < 256; i++)
    {
        if (callback_functions[i] == NULL)
            callback_functions[i] = &deffault_func;
    }
}

int counter = 0;
bool isInit = false;

void setup()
{
    Serial.begin(115200);
    Serial.println("\n-- PAMI test --\n");
    isInit = com->begin(SS, RST, BUSY);
    // leftMotor.init();
    // leftMotor.enableMotor(true);
    // leftMotor.setAcceleration(100.0f);

    // rightMotor.init();
    // rightMotor.enableMotor(true);
    // rightMotor.setAcceleration(100.0f);

    Serial.println("Motors initialized");

#if ENABLE_OTA
    ota.begin();
    server.begin();
#endif
    initialize_callback_functions();
}


void loop()
{
    // rightMotor.update();
    // leftMotor.update();

    // if (counter++ > 1024)
    // {
    //     counter = 0;
    //     com->print("Hello world");
    //     Serial.println("Hello world");
    // }
    if (isInit)
        com->handle_callback(callback_functions);
    else if (counter++ > 40096) {
        counter = 0;
        isInit = com->begin(SS, RST, BUSY);
    }
#if ENABLE_OTA
    ota.loop();
#endif
}
