#include "config.h"

Motor *leftMotor = new Motor(LEFT_STEP_PIN, LEFT_DIR_PIN, LEFT_EN_PIN, LEFT_STEPS_PER_REV, K, true);
Motor *rightMotor = new Motor(RIGHT_STEP_PIN, RIGHT_DIR_PIN, RIGHT_EN_PIN, RIGHT_STEPS_PER_REV, K);

RollingBasis *rollingBasis = new RollingBasis(leftMotor, rightMotor, WHEEL_DIAMETER_MM, WHEEL_BASE_MM, Point{0, 0, 0});

Navigation *navigation = new Navigation(rollingBasis, 15000); // Navigation object with 100ms interval and 15s timeout

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

hw_timer_t *MovementTimer = NULL;
hw_timer_t *lidarTimer = NULL;

TaskHandle_t MovementTask = NULL; // Task handle for movement updates
TaskHandle_t LidarTask = NULL;    // Task handle for movement updates

int d_zero, d_on = 0;

// Array to store points to navigate to
Point strat[] = {
    {0, 100, 0},
    {100, 100, 0},
    {100, 0, 0},
    {0, 0, 0}};
int currentIndex = 0; // Current index in the strats array
bool ACS = false;
bool oldACS = false;

bool canStart = false; // Flag to indicate if navigation can start

void navigationUpdate()
{
    navigation->update(); // Update rolling basis
    if (ACS)
    {
        if (oldACS != ACS)
        {
            Serial.println("ACS activated, stopping rolling basis.");
            oldACS = ACS;   // Update oldACS to current ACS state
            currentIndex--; // Decrement index if ACS is true
            if (currentIndex < 0)
            {
                currentIndex = 0; // Prevent index from going negative
            }
        }
        navigation->stop(); // Stop rolling basis if ACS is true
    }
    else if (!navigation->isMoving())
    {
        if (currentIndex < sizeof(strat) / sizeof(strat[0]))
        {
            navigation->setCommand(strat[currentIndex]);
            Serial.print("Setting command to: ");
            Serial.println(strat[currentIndex].x);
            currentIndex++;
        }
        else
        {
            Serial.println("All points navigated, stopping navigation.");
            navigation->stop(); // Stop navigation if all points are navigated
            // start SERVO
        }
    }
}

void lidarUpdate()
{
    if (lidar->obstacleAhead(ACS_TRESHOLD)) // Check if an obstacle is ahead
    {
        ACS = true; // Activate ACS if an obstacle is detected
    }
    else
    {
        ACS = false; // Deactivate ACS if no obstacle is detected
    }
}

void setup()
{
    setCpuFrequencyMhz(240);

    Serial.begin(115200);
    Serial.println("\n-- PAMI test --\n");

    lidar->begin(lidar_pami::DEFAULT_BAUD); // Initialize LIDAR
    lidar->onReceive([]()
                     {
        if (!canStart){
            if (!lidar->isTiretteOn()) // Check if tirette is on
            {
                canStart = true; // Set canStart to true if tirette is on
                Serial.println("Tirette activated, starting navigation.");
            }
        } else {
            lidarUpdate(); // Call lidar update function when data is received
        } });
    Serial.println("LIDAR initialized");
    delay(100); // Wait for LIDAR to stabilize
#if ENABLE_OTA
    Serial.println("OTA enabled");
    ota.begin();
    server.begin();
#endif
#if ENABLE_LORA
    isInit = com->begin(SS, RST, BUSY);
    // initialize_callback_functions();
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
    // MovementTimer = timerBegin(0, 24000, true);                   // Create a timer with 8000 prescaler (80MHz / 8000 = 10kHz)
    // timerAttachInterrupt(MovementTimer, &navigationUpdate, true); // Attach the interrupt function
    // timerAlarmWrite(MovementTimer, 50, true);                     // Count to 100 in order to trigger the interrupt. (10kHz / 50 = 200Hz)
    // timerAlarmEnable(MovementTimer);                              // Enable the timer interrupt

    // create a second timer for lidar update
    // lidarTimer = timerBegin(1, 24000, true);               // Create a second timer with 8000 prescaler
    // timerAttachInterrupt(lidarTimer, &lidarUpdate, true); // Attach the interrupt function for lidar
    // timerAlarmWrite(lidarTimer, 1000, true);              // Count to 1000 in order to trigger the interrupt. (10kHz / 1000 = 10Hz)
    // timerAlarmEnable(lidarTimer);                         // Enable the lidar timer interrupt
    // Serial.println("Setup complete, starting navigation...");
}

long lastTime = 0; // Variable to store the last time the loop was executed
void loop()
{
    if (millis() - lastTime > 2 && canStart) // Check if 2ms have passed since the last navigation update
    {
        navigationUpdate(); // Call navigation update function
    }
    lidar->loop();
    lastTime = millis();
#if ENABLE_OTA
    ota.loop();
#endif
#if ENABLE_LORA
    if (isInit)
    {

    } // com->handle_callback(callback_functions);
    else
    {
        isInit = com->begin(SS, RST, BUSY);
        if (isInit)
        {
            Serial.println("LoRa re-initialized");
        }
        else
        {
            Serial.println("LoRa re-initialization failed");
        }
    }

#endif
}
