#include "config.h"
#include "strategy.h"
#include "relative_forward.h"
#include "navigation.h"
#include "AtoB.h"

Motor* leftMotor = nullptr;
Motor* rightMotor = nullptr;
RollingBasis* rollingBasis = nullptr;
Navigation* navigation = nullptr;
Strategy* strategy = nullptr;

AtoB* action = new AtoB(rollingBasis, {200, 0, 0});
std::vector<Point> strat = {{0, 100, 0}};  
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
        if (oldACS)
            return;
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
    Serial.begin(115200);
    while (!Serial) { delay(100); }
    delay(1000);
    Serial.println("\n--- DEBUG START ---");
    
    action->start();  // AtoB direct, pas Strategy
    canStart = true;
}

long lastTime = 0;  // Variable to store the last time the update was executed

void loop() {
    leftMotor->update();
    rightMotor->update();

    if (millis() - lastTime > 2 && canStart) {
        strategy->strategie_update();
        lastTime = millis();

        if (strategy->isFinished()) {
            Serial.println("Strategy finished!");
            canStart = false;
        }
    }
}
