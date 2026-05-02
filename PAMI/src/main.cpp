#include "blocking_forward.h"
#include "blocking_turn.h"
#include "config.h"
#include "go_to.h"
#include "strategy.h"

#if ENABLE_OTA
#include "OTA.h"
AsyncWebServer server(80);
CustomOTA ota(OTA_WIFI_SSID,
              OTA_WIFI_PASSWORD,
              OTA_HOSTNAME,
              OTA_FALLBACK_AP_SSID,
              OTA_FALLBACK_AP_PASSWORD,
              &server);
#endif

Motor* leftMotor = new Motor(LEFT_STEP_PIN,
                             LEFT_DIR_PIN,
                             LEFT_EN_PIN,
                             LEFT_STEPS_PER_REV,
                             PULSE_US,
                             false);

Motor* rightMotor = new Motor(RIGHT_STEP_PIN,
                              RIGHT_DIR_PIN,
                              RIGHT_EN_PIN,
                              RIGHT_STEPS_PER_REV,
                              PULSE_US,
                              true);

RollingBasis* rollingBasis = new RollingBasis(leftMotor,
                                              rightMotor,
                                              WHEEL_DIAMETER_MM,
                                              WHEEL_BASE_MM,
                                              Point{0.0f, 0.0f, 0.0f});

/*
Navigation* navigation = new Navigation(rollingBasis, 15000);
//lidar_pami* lidar = new lidar_pami(Serial0);
Strategy* strategy = new Strategy(rollingBasis);

#if ENABLE_OTA
#include "OTA.h"
AsyncWebServer server(80);
CustomOTA ota("DVB", "davincibot", &server);
#endif
#if ENABLE_LORA
#include "com_pami.h"
Com* com = new Com();
bool isInit = false;
#endif

hw_timer_t* MovementTimer = NULL;
hw_timer_t* lidarTimer = NULL;

TaskHandle_t MovementTask = NULL;
TaskHandle_t LidarTask = NULL;

int d_zero, d_on = 0;
bool tirette, t_one, t_two = true;

std::vector<Point> strat = {
    {100, 100, 0}
};

int currentIndex = 0;
bool ACS = false;
bool oldACS = false;

bool canStartTimer = true;
long startTimer = 276447230;

long dt = 0;
long lastTimerrrr = 0;

void navigationUpdate() {
    navigation->update();
    if (ACS) {
        if (oldACS) return;
        oldACS = ACS;
        navigation->stop();
        Serial.println("ACS activated - Navigation stopped!");
    } else {
        oldACS = ACS;
    }
}
*/

Strategy* strategy = new Strategy(rollingBasis);

bool strategyRunning = false;
bool strategyDoneLogged = false;
unsigned long lastStrategyUpdateMs = 0;
bool canStart = false;

void setup() {
    Serial.begin(115200);
    while (!Serial) {
        delay(100);
    }

    delay(2000);
    Serial.println("\n--- DEMARRAGE ---");

#if ENABLE_OTA
    ota.begin();
#endif

    // rollingBasis->moveForwardBlocking(100.0f);
    strategy->addAction(new BlockingForward(rollingBasis, 100.0f));
    strategy->addAction(new GoTo(rollingBasis, Point{100.0f, 0.0f, 1.5708f}));
    strategy->addAction(new BlockingTurn(rollingBasis, -1.5708f));
    strategy->start();

    strategyRunning = true;
}

void loop() {
#if ENABLE_OTA
    ota.loop();
#endif

    leftMotor->update();
    rightMotor->update();

    // Serial.printf("[Main loop] Pose: (%.1f, %.1f, %.3f) mm rad\n",
    //               rollingBasis->getPose().x, rollingBasis->getPose().y,
    //               rollingBasis->getPose().theta);

    if (!strategyRunning) {
        return;
    }

    if (millis() - lastStrategyUpdateMs >= 2) {
        strategy->update();
        lastStrategyUpdateMs = millis();
    }

    if (strategy->isFinished() && !strategyDoneLogged) {
        Serial.println("--- STRATEGY TERMINEE ---");
        strategyRunning = false;
        strategyDoneLogged = true;
    }
}
