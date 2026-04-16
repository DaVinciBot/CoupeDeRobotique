#include "config.h"
#include "strategy.h"
#include <vector>

Motor* leftMotor = new Motor(LEFT_STEP_PIN,       // Broche 19
                             LEFT_DIR_PIN,        // Broche 18
                             LEFT_EN_PIN,         // Broche enable
                             LEFT_STEPS_PER_REV,  // Steps par tour
                             PULSE_US,
                             false);

Motor* rightMotor = new Motor(RIGHT_STEP_PIN,       // Broche 17
                              RIGHT_DIR_PIN,        // Broche 16
                              RIGHT_EN_PIN,         // Broche enable
                              RIGHT_STEPS_PER_REV,  // Steps par tour
                              PULSE_US,
                              true);

RollingBasis* rollingBasis = new RollingBasis(leftMotor,
                                              rightMotor,
                                              WHEEL_DIAMETER_MM,
                                              WHEEL_BASE_MM,
                                              Point{0, 0, 0});  // Initial position (x, y, theta)

Navigation* navigation = new Navigation(
    rollingBasis,
    15000);  // Navigation object with 100ms interval and 15s timeout

//lidar_pami* lidar = new lidar_pami(Serial0);  // LIDAR object

#if ENABLE_OTA
#include "OTA.h"
AsyncWebServer server(80);
CustomOTA ota("DVB", "davincibot", &server);
#endif
#if ENABLE_LORA
#include "com_pami.h"
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
// Définir la trajectoire
std::vector<Point> strat = {
    {100, 100, 0} 
};

int currentIndex = 0;  // Current index in the strats array
bool ACS = false;
bool oldACS = false;

bool canStartTimer = true;
long startTimer = 276447230;
bool canStart = false;  // Flag to indicate if navigation can start

long dt = 0;
long lastTimerrrr = 0;



void navigationUpdate() {
    navigation->update();  // Navigation gère automatiquement tous les waypoints
    
    if (ACS) {
        if (oldACS) return;
        oldACS = ACS;
        navigation->stop();
        Serial.println("ACS activated - Navigation stopped!");
    } else {
        oldACS = ACS;
    }
}

/*void lidarUpdate() {
    if (lidar->obstacleAhead(ACS_TRESHOLD))  // Check if an obstacle is ahead
    {
        ACS = true;  // Activate ACS if an obstacle is detected
    } else {
        ACS = false;  // Deactivate ACS if no obstacle is detected
    }
}*/

void setup() {
    delay(5000);  // pour le serial monitor
    setCpuFrequencyMhz(240);

    Serial.begin(115200);
    delay(500);   // Attendre que le Serial soit vraiment prêt
    Serial.println("\n-- PAMI test --\n");
    // Charger la trajectoire complète
    navigation->setTrajectory(strat);
    
    

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
    //isInit = com->begin(SS, RST, BUSY);
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
    static Strategy* strategy = nullptr;
    static bool initialized = false;
    static bool finished_printed = false;

    if (!initialized) {
        lastTime = millis();
        
        // Créer la stratégie avec une trajectoire de 3 points
        strategy = new Strategy(rollingBasis);
        
        std::vector<Point> trajectory = {
            Point{100.0, 0.0, 0.0},      // Point 1
            Point{100.0, 100.0, 0.0},    // Point 2
            Point{0.0, 100.0, 0.0}       // Point 3
        };
        
        // Utiliser la nouvelle fonction
        strategy->creer_strategie(trajectory);
        strategy->start();
        Serial.println("=== Strategy with 3 points ===");
        initialized = true;
    }

    rightMotor->update();
    leftMotor->update();
    if (millis() - lastTime > 2) {
        // Utiliser la nouvelle fonction qui fait tout (moteurs + stratégie)
        strategy->strategie_update();
        lastTime = millis();
    }

    if (strategy->isFinished() && !finished_printed) {
        strategy->stop();
        Serial.println("=== Strategy FINISHED ===");
        finished_printed = true;
    }
}

/*void loop() {
    

    leftMotor->update();
    rightMotor->update();

    // navigation : toutes les 5ms suffit
    if (millis() - lastTime > 2) {
        navigationUpdate();  // Appel de navigationUpdate qui gère tout
        lastTime = millis();
    }
    //lidar->update();
#if ENABLE_OTA
    ota.loop();
#endif
#if ENABLE_LORA
    if (isInit) {
    }  // com->handle_callback(callback_functions);
    else {
        //isInit = com->begin(SS, RST, BUSY);
        if (isInit) {
            //Serial.println("LoRa re-initialized");
        } else {
            //Serial.println("[ERROR] LoRa re-initialization failed");
        }
    }

#endif
}*/