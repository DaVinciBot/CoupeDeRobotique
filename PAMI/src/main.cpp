#include "config.h"

Motor *leftMotor = new Motor(LEFT_STEP_PIN, LEFT_DIR_PIN, LEFT_EN_PIN, LEFT_STEPS_PER_REV, K);
Motor *rightMotor = new Motor(RIGHT_STEP_PIN, RIGHT_DIR_PIN, RIGHT_EN_PIN, RIGHT_STEPS_PER_REV, K);

PID linearDistancePid(LINEAR_DISTANCE_KP, LINEAR_DISTANCE_KI, LINEAR_DISTANCE_KD, 0.01f);
PID angularDistancePid(ANGULAR_DISTANCE_KP, ANGULAR_DISTANCE_KI, ANGULAR_DISTANCE_KD, 0.01f);

RollingBasis *rollingBasis = new RollingBasis(leftMotor, rightMotor, WHEEL_DIAMETER_MM, WHEEL_BASE_MM, linearDistancePid, angularDistancePid, Point{0, 0, 0});

lidar_pami *lidar = new lidar_pami(Serial0); // LIDAR object

#if ENABLE_OTA
#include "OTA.h"
AsyncWebServer server(80);
CustomOTA ota("DVB", "davincibot", &server);
#endif
#if ENABLE_LORA
#include "com.h"
Com *com = new Com(); // LoRa object
bool isInit = false;
#endif

hw_timer_t *timer = NULL;

void rollingBasisUpdate()
{
    return;
}

void setup()
{
    Serial.begin(115200);
    Serial.println("\n-- PAMI test --\n");

    // leftMotor->init();
    // rightMotor->init();
    // leftMotor->enableMotor(true);
    // rightMotor->enableMotor(true);
    // leftMotor->setAcceleration(100.0f);  // Set target speed for left motor
    // rightMotor->setAcceleration(100.0f); // Set target speed for left motor
    // Serial.println("Motors initialized");

    // leftMotor->setTargetSpeed(1000.0f);   // Set target speed for left motor
    // rightMotor->setTargetSpeed(-1000.0f); // Set target speed for left motor

    rollingBasis->setCommand(Point{0, 100, 0}); // Set target position for rolling basis

    lidar->begin(lidar_pami::DEFAULT_BAUD); // Initialize LIDAR
    Serial.println("LIDAR initialized");
    delay(1000); // Wait for LIDAR to stabilize

    // Check if LIDAR is ready
    if (lidar->obstacleAhead(100))
    {
        Serial.println("Obstacle detected within 100mm");
    }
    else
    {
        Serial.println("No obstacle detected");
    }
#if ENABLE_OTA
    Serial.println("OTA enabled");
    ota.begin();
    server.begin();
#endif
#if ENABLE_LORA
    isInit = com->begin(SS, RST, BUSY);
    initialize_callback_functions();
    if (isInit)
    {
        Serial.println("LoRa initialized");
    }
    else
    {
        Serial.println("LoRa initialization failed");
    }
#else
    Serial.println("LoRa not enabled");
#endif

    // rolling basis update 100hz (80Mhz / 8000 / 100 = 100Hz)
    // timer = timerBegin(0, 8000, true);                      // Create a timer with 8000 prescaler (80MHz / 8000 = 10kHz)
    // timerAttachInterrupt(timer, &rollingBasisUpdate, true); // Attach the interrupt function
    // timerAlarmWrite(timer, 100, true);                      // Count to 100 in order to trigger the interrupt. (10kHz / 100 = 100Hz)
    // timerAlarmEnable(timer);                                // Enable the timer interrupt
}

int current_speed = 0;
bool decreasing = false;

void loop()
{
    for (size_t i = 0; i < 100; i++)
    {
        // leftMotor->update();  // Update left motor
        // rightMotor->update(); // Update right motor
        rollingBasis->update(); // Update rolling basis
    }

#if ENABLE_OTA
    ota.loop();
#endif
#if ENABLE_LORA
    if (isInit)
        com->handle_callback(callback_functions);
#endif
}
