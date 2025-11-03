#include "config.h"

Motor* testMotor = new Motor(LEFT_STEP_PIN,  // Broche 19
                          LEFT_DIR_PIN,    // Broche 18
                          LEFT_EN_PIN,     // Broche enable
                          200,             // Steps par tour (typique pour un NEMA)
                          false);

// Pour debug
const int numSteps = 800;  // Nombre de pas à faire
                              

/*RollingBasis* rollingBasis = new RollingBasis(leftMotor,
                                              rightMotor,
                                              WHEEL_DIAMETER_MM,
                                              WHEEL_BASE_MM,
                                              Point{0, 0, 0});

Navigation* navigation = new Navigation(
    rollingBasis,
    15000);  // Navigation object with 100ms interval and 15s timeout

lidar_pami* lidar = new lidar_pami(Serial0);  // LIDAR object*/

#if ENABLE_OTA
#include "OTA.h"
AsyncWebServer server(80);
CustomOTA ota("DVB", "davincibot", &server);
#endif
#if ENABLE_LORA
#include "com.h"
Com* com = new Com();  // LoRa object
bool isInit = false;
#endif

hw_timer_t* MovementTimer = NULL;
hw_timer_t* lidarTimer = NULL;

TaskHandle_t MovementTask = NULL;  // Task handle for movement updates
TaskHandle_t LidarTask = NULL;     // Task handle for movement updates

int d_zero, d_on = 0;
bool tirette, t_one, t_two = true;

// Array to store points to navigate to
Point strat[] = {{0, 100, 0}, {100, 100, 0}, {100, 0, 0}, {0, 0, 0}};
int currentIndex = 0;  // Current index in the strats array
bool ACS = false;
bool oldACS = false;

bool canStartTimer = true;
long startTimer = 276447230;
bool canStart = false;  // Flag to indicate if navigation can start

long dt = 0;
long lastTimerrrr = 0;
/*
void navigationUpdate() {
    navigation->update();  // Update rolling basis
    if (ACS) {
        if (oldACS)
            return;
        Serial.println("ACS activated, stopping rolling basis.");
        oldACS = ACS;    // Update oldACS to current ACS state
        currentIndex--;  // Decrement index if ACS is true
        if (currentIndex < 0) {
            currentIndex = 0;  // Prevent index from going negative
        }
        navigation->stop();  // Stop rolling basis if ACS is true
    } else {
        oldACS = ACS;  // Update oldACS to current ACS state
        if (dt < 20000) {
            leftMotor->setTargetSpeed(4000.0f * 3);
            rightMotor->setTargetSpeed(4000.0f);
            dt += millis() - lastTimerrrr;
            lastTimerrrr = millis();
        } else {
            Serial.println("All points navigated, stopping navigation.");
            navigation->stop();  // Stop navigation if all points are navigated
                                 // start SERVO
        }
    }
}

void lidarUpdate() {
    if (lidar->obstacleAhead(ACS_TRESHOLD))  // Check if an obstacle is ahead
    {
        ACS = true;  // Activate ACS if an obstacle is detected
    } else {
        ACS = false;  // Deactivate ACS if no obstacle is detected
    }
}*/

void setup() {
    Serial.begin(115200);
    Serial.println("\n-- Test Moteur --\n");
    Serial.printf("STEP_PIN: %d, DIR_PIN: %d, EN_PIN: %d\n", 
                 LEFT_STEP_PIN, LEFT_DIR_PIN, LEFT_EN_PIN);
    
    // Configuration des broches
    testMotor->init();
    testMotor->enableMotor(true);  // Active le moteur
    
    Serial.println("Moteur initialisé");

    /*lidar->begin(lidar_pami::DEFAULT_BAUD);  // Initialize LIDAR
    lidar->onReceive([]() {
        if (!canStart) {
            t_two = t_one;
            t_one = tirette;                   // Update tirette state
            tirette = lidar->isTiretteOn();    // Check if tirette is on
            if (!(tirette || t_one || t_two))  // Check if tirette is on
            {
                // canStartTimer = true; // Set canStart to true if tirette is
                // on
                canStart = true;
                Serial.println("Tirette activated, starting navigation.");
            }
            Serial.println("Waiting for tirette activation...");
        } else {
            lidarUpdate();  // Call lidar update function when data is received
        }
    });*/
    Serial.println("LIDAR initialized");
    delay(100);  // Wait for LIDAR to stabilize
#if ENABLE_OTA
    Serial.println("OTA enabled");
    ota.begin();
    server.begin();
#endif
#if ENABLE_LORA
    isInit = com->begin(SS, RST, BUSY);
    // initialize_callback_functions();
    if (isInit) {
        Serial.println("LoRa initialized");
    } else {
        Serial.println("[ERROR] LoRa initialization failed");
    }
#else
    Serial.println("LoRa not enabled");
#endif
    // MovementTimer = timerBegin(0, 24000, true);                   // Create a
    // timer with 8000 prescaler (80MHz / 8000 = 10kHz)
    // timerAttachInterrupt(MovementTimer, &navigationUpdate, true); // Attach
    // the interrupt function timerAlarmWrite(MovementTimer, 50, true); // Count
    // to 100 in order to trigger the interrupt. (10kHz / 50 = 200Hz)
    // timerAlarmEnable(MovementTimer);                              // Enable
    // the timer interrupt

    // create a second timer for lidar update
    // lidarTimer = timerBegin(1, 24000, true);               // Create a second
    // timer with 8000 prescaler timerAttachInterrupt(lidarTimer, &lidarUpdate,
    // true); // Attach the interrupt function for lidar
    // timerAlarmWrite(lidarTimer, 1000, true);              // Count to 1000 in
    // order to trigger the interrupt. (10kHz / 1000 = 10Hz)
    // timerAlarmEnable(lidarTimer);                         // Enable the lidar
    // timer interrupt Serial.println("Setup complete, starting navigation...");
}

long lastTime = 0;  // Variable to store the last time the update was executed
void loop() {
    
    // Fait tourner le moteur comme dans votre code original
    
    testMotor->doOneSteps(); //marche avec k=1          
    delayMicroseconds(1e5);  // Même délai que votre code original
    
#if ENABLE_OTA
    ota.loop();
#endif
#if ENABLE_LORA
    if (isInit) {
    }  // com->handle_callback(callback_functions);
    else {
        isInit = com->begin(SS, RST, BUSY);
        if (isInit) {
            Serial.println("LoRa re-initialized");
        } else {
            Serial.println("[ERROR] LoRa re-initialization failed");
        }
    }

#endif
}
