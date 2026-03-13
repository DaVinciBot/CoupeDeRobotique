#include "config.h"

// LIDAR
lidar_pami* lidar = new lidar_pami(Serial2,  // Port série UART
                                    16,      // RX pin 
                                    17);     // TX pin

bool ACS = false;

// ===== COMMENTED OUT FOR LIDAR TESTING =====
/*
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

Motor* leftMotor = new Motor(LEFT_STEP_PIN, LEFT_DIR_PIN, LEFT_EN_PIN, LEFT_STEPS_PER_REV, PULSE_US, true);
Motor* rightMotor = new Motor(RIGHT_STEP_PIN, RIGHT_DIR_PIN, RIGHT_EN_PIN, RIGHT_STEPS_PER_REV, PULSE_US, false);
RollingBasis* rollingBasis = new RollingBasis(leftMotor, rightMotor, WHEEL_DIAMETER_MM, WHEEL_BASE_MM, Point{0, 0, 0});
Navigation* navigation = new Navigation(rollingBasis, 15000);

hw_timer_t* MovementTimer = NULL;
hw_timer_t* lidarTimer = NULL;
TaskHandle_t MovementTask = NULL;
TaskHandle_t LidarTask = NULL;

int d_zero, d_on = 0;
bool tirette, t_one, t_two = true;
Point strat[] = {{0, 100, 0}, {100, 100, 0}, {100, 0, 0}, {0, 0, 0}};
int currentIndex = 0;
bool oldACS = false;
bool canStartTimer = true;
long startTimer = 276447230;
bool canStart = false;
long dt = 0;
long lastTimerrrr = 0;
*/

/*void navigationUpdate() {
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
}*/

void lidarUpdate() {
    // Print radar visualization
    //lidar->printRadarVisual();
    
    // Check for obstacle directly ahead at 20cm
    if (lidar->obstacleDirectlyAhead(200))  // 200mm = 20cm
    {
        //Serial.println("OBSTACLE");
        ACS = true;
    } else {
        //Serial.println("NO OBSTACLE");
        ACS = false;
    }
}

void setup() {
    delay(1000);
    Serial.begin(115200);
    lidar->begin(lidar_pami::DEFAULT_BAUD);
    lidar->onReceive([]() {
        lidarUpdate();
    });
    delay(10000);
    //il s'identifie (avant la 85eme s)
    String str_identifier="";
    int obstacle_compteur=0;
    for(int cote=0;cote<4;cote++){//boucle pour chaque coté
        obstacle_compteur=0;
        for(int i=0; i<100;i++){ //on prend un échantillon de 100 update pour etre sur
            lidar->update();
            //Serial.println(ACS);
            if(ACS){
                obstacle_compteur++;
            }
            delay(5);//il met environ 1s par boucle par 5 de delay
        }
        if(obstacle_compteur>80){ //il est sur à 80% qu'il y a un obstacle
            //Serial.println("Obstacle, on tourne");
            str_identifier+="1";
        }
        else{
            //Serial.println("c ok");
            str_identifier+="0";
        }
        Serial.println(str_identifier);
        Serial.println("Turning 90 degrees");
        delay(1000); // Simulate time taken to turn 90 degrees
        //on tourne de 90° pour le prochain coté
    }
    //mtn, on exploite son identifier pour savoir ou il est
    if(NUMBER_OF_PAMIS==6){ //on regarde de gauche à droite de haut en bas depuis mon dessin
        if (str_identifier == "0011") {
            Serial.println("PAMI 1");
        } else if (str_identifier == "1011") {
            Serial.println("PAMI 2");
        } else if (str_identifier == "0111") {
            Serial.println("PAMI 3");
        } else if (str_identifier == "1111") {
            Serial.println("PAMI 4");
        } else if (str_identifier == "0110") {
            Serial.println("PAMI 5");
        } else if (str_identifier == "1110") {
            Serial.println("PAMI 6");
        } else {
            Serial.println("Unknown PAMI identifier: " + str_identifier);
        }
    }
    if(NUMBER_OF_PAMIS==4){ //on regarde de gauche à droite
        if (str_identifier == "1110") {
            Serial.println("PAMI 1");
        } else if (str_identifier == "1111") {
            Serial.println("PAMI 2");
        } else if (str_identifier == "0110") {
            Serial.println("PAMI 3");
        } else if (str_identifier == "0111") {
            Serial.println("PAMI 4");
        } else {
            Serial.println("Unknown PAMI identifier: " + str_identifier);
        }
    }
}


void loop() {
    lidar->update();
    
    
}
