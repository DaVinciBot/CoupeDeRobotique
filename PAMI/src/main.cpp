#include "blocking_forward.h"
#include "blocking_turn.h"
#include "actionneur_sweep.h"
#include "config.h"
#include "go_to.h"
#include "lidar_pami.h"
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

#if ENABLE_LORA
HardwareSerial LoRaSerial(2);
char loraRxBuffer[256];
int loraRxPos = 0;
int myPamiId = -1;
#endif

HardwareSerial LidarSerial(1);
lidar_pami* lidar =
    new lidar_pami(LidarSerial, LIDAR_RX_PIN, LIDAR_TX_PIN, true);

volatile bool acsBlocked = false;

void lidarTask(void* param) {
    lidar_pami* lid = (lidar_pami*)param;
    for (;;) {
        lid->update();
        acsBlocked = lid->obstacleDirectlyAhead(ACS_TRESHOLD);
        vTaskDelay(pdMS_TO_TICKS(5));
    }
}

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

RollingBasis* rollingBasis = new RollingBasis(rightMotor,
                                              leftMotor,
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

#if ENABLE_LORA
void purgeLoRa() {
    LoRaSerial.print("\n");
    LoRaSerial.flush();
    delay(100);
    while (LoRaSerial.available()) {
        LoRaSerial.read();
    }
    loraRxPos = 0;
}

void sendIdRequest() {
    Serial.println(">> LoRa: envoi demande d'ID (cmd 1)");
    LoRaSerial.print("1\n");
}

void handleIdAttribution(char** tokens, int nbTokens) {
    if (nbTokens < 2) return;
    if (myPamiId != -1) {
        Serial.printf("LoRa: ID deja attribue (%d), ignore.\n", myPamiId);
        return;
    }
    myPamiId = atoi(tokens[1]);
    Serial.printf(">> LoRa: ID attribue = %d\n", myPamiId);
}

void handleDepotAssignment(char** tokens, int nbTokens) {
    if (myPamiId == -1) {
        Serial.println("LoRa: cmd 3 recue mais pas d'ID -> ignoree");
        return;
    }

    for (int i = 1; i + 2 < nbTokens; i += 3) {
        int id = atoi(tokens[i]);
        if (id == myPamiId) {
            float x = atof(tokens[i + 1]);
            float y = atof(tokens[i + 2]);

            Serial.printf(">> LoRa: depot recu -> x=%.1f mm, y=%.1f mm\n", x,
                          y);

            strategy->clearActions();
            strategy->addAction(
                new GoTo(rollingBasis, Point{x, y, 0.0f}));
            strategy->start();
            strategyRunning = true;
            strategyDoneLogged = false;

            Serial.println(">> LoRa: nouvelle strategy GoTo lancee");
            return;
        }
    }

    Serial.println("LoRa: aucun depot pour mon ID dans cmd 3");
}

void parseLoRaMessage(char* msg) {
    Serial.printf("[LoRa RX] %s\n", msg);

    const int MAX_TOKENS = 64;
    char* tokens[MAX_TOKENS];
    int nbTokens = 0;

    char* p = strtok(msg, "|");
    while (p != NULL && nbTokens < MAX_TOKENS) {
        tokens[nbTokens++] = p;
        p = strtok(NULL, "|");
    }
    if (nbTokens == 0) return;

    int cmd = atoi(tokens[0]);
    switch (cmd) {
        case 2: handleIdAttribution(tokens, nbTokens); break;
        case 3: handleDepotAssignment(tokens, nbTokens); break;
        default: break;
    }
}

void handleLoRaInput() {
    while (LoRaSerial.available()) {
        char c = LoRaSerial.read();
        if (c == '\n') {
            loraRxBuffer[loraRxPos] = '\0';
            if (loraRxPos > 0) parseLoRaMessage(loraRxBuffer);
            loraRxPos = 0;
        } else if (c == '\r') {
            // ignore
        } else if (loraRxPos < (int)sizeof(loraRxBuffer) - 1) {
            loraRxBuffer[loraRxPos++] = c;
        } else {
            loraRxPos = 0;
        }
    }
}
#endif

void setup() {
    Serial.begin(115200);
    while (!Serial) {
        delay(100);
    }

    delay(2000);
    DEBUG_PRINTLN("\n--- DEMARRAGE ---");

    lidar->begin();
    xTaskCreatePinnedToCore(lidarTask, "lidar", 4096, lidar, 1, NULL, 0);
    DEBUG_PRINTLN("Lidar task started on core 0");

    // Tirette: attendre qu'elle soit branchée puis retirée
    pinMode(TIRETTE_PIN, INPUT_PULLDOWN);
    DEBUG_PRINTLN("Attente tirette...");
    // Attendre que la tirette soit connectée (pin HIGH)
    while (digitalRead(TIRETTE_PIN) == LOW) {
        delay(50);
    }
    DEBUG_PRINTLN("Tirette connectee, attente retrait...");
    // Attendre que la tirette soit retirée (pin LOW)
    while (digitalRead(TIRETTE_PIN) == HIGH) {
        delay(50);
    }
    DEBUG_PRINTLN("Tirette retiree, GO!");

#if ENABLE_OTA
    ota.begin();
#endif

#if ENABLE_LORA
    LoRaSerial.begin(LORA_BAUD, SERIAL_8N1, LORA_RX_PIN, LORA_TX_PIN);
    purgeLoRa();
    Serial.println("LoRa: demande d'ID au Calcul Deporte...");
    sendIdRequest();
    while (myPamiId == -1) {
        handleLoRaInput();
        delay(10);
    }
    Serial.printf("LoRa: ID recu = %d, demarrage strategy.\n", myPamiId);
#endif

    // rollingBasis->moveForwardBlocking(100.0f);
    if(ENABLE_HOMOLOGATION){
        strategy->addAction(new BlockingForward(rollingBasis, 1400.0f));
        strategy->addAction(new ActionneurSweep(SERVO_PIN, 25000));
        strategy->start();
    }else{
        
    }

    strategyRunning = true;
}

void loop() {
#if ENABLE_OTA
    ota.loop();
#endif

    leftMotor->update();
    rightMotor->update();

#if ENABLE_LORA
    handleLoRaInput();
#endif

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
        DEBUG_PRINTLN("--- STRATEGY TERMINEE ---");
        strategyRunning = false;
        strategyDoneLogged = true;
    }
}
