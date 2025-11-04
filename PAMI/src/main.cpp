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
    // Test sequence state machine: exercises several Motor methods so you can
    // observe their effects on the driver and on the logical step counter.
    static int phase = 0;
    static unsigned long phaseStart = 0;
    unsigned long now = millis();

    // Phases:
    // 0 = single-step test (call doOneSteps slowly)
    // 1 = enable/disable toggle
    // 2 = forward with setTargetSpeed + acceleration
    // 3 = reset counter and reverse briefly
    // 4 = report and loop
    if (phase == 0) {
        if (phaseStart == 0) {
            phaseStart = now;
            Serial.println("Phase 0: single-step test (doOneSteps)");
        }
        testMotor->doOneSteps();
        delayMicroseconds(100000);  // 100 ms between single steps
        if (now - phaseStart >= 3000) {  // run this phase for 3s
            Serial.printf("Counts after single-step phase: %ld\n", testMotor->getStepCount());
            phaseStart = now;
            phase = 1;
        }
    } else if (phase == 1) {
        if (phaseStart == now) {
            /* no-op */
        }
        Serial.println("Phase 1: toggling enable off then on");
        testMotor->enableMotor(false);
        delay(500);
        testMotor->enableMotor(true);
        Serial.println("Enable toggle complete");
        phase = 2;
        phaseStart = now;
    } else if (phase == 2) {
        if (phaseStart == now) {
            Serial.println("Phase 2: forward run with setTargetSpeed(200)");
            testMotor->setAcceleration(1000.0f);
            testMotor->setTargetSpeed(200.0f);
            phaseStart = now;
        }
        // let update() drive the motor for 3s
        testMotor->update();
        delay(2);
        if (now - phaseStart >= 3000) {
            testMotor->setTargetSpeed(0);
            Serial.printf("Counts after forward run: %ld\n", testMotor->getStepCount());
            phase = 3;
            phaseStart = now;
        }
    } else if (phase == 3) {
        Serial.println("Phase 3: reset counter and reverse briefly");
        testMotor->resetStepCount();
        Serial.printf("Count after reset: %ld\n", testMotor->getStepCount());
        testMotor->setAcceleration(1000.0f);
        testMotor->setTargetSpeed(-200.0f);
        unsigned long end = millis() + 2000;
        while (millis() < end) {
            testMotor->update();
            delay(2);
        }
        testMotor->setTargetSpeed(0);
        Serial.printf("Counts after reverse run: %ld\n", testMotor->getStepCount());
        phase = 4;
        phaseStart = now;
    } else if (phase == 4) {
        Serial.println("Phase 4: report");
        Serial.printf("Steps per rev (logical): %u\n", testMotor->getStepsPerRev());
        Serial.printf("isMoving(): %d\n", testMotor->isMoving());
        Serial.printf("Final step count: %ld\n", testMotor->getStepCount());
        // loop back to phase 0 after short pause
        delay(500);
        phase = 0;
        phaseStart = 0;
    }
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
