#include "config.h"
#include "AtoB.h"

// --- COMMENTE POUR LE TEST ---
// #include "strategy.h"
// #include "navigation.h"
// #include <vector>

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


// --- CREATION DE L'ACTION DE TEST ---
// On crée une action AtoB ciblant 300mm en X, 0 en Y, et 0 en angle.
AtoB* testAction = new AtoB(rollingBasis, Point{0.0, 300.0, 0.0});


// --- TOUT CE BLOC EST COMMENTE POUR LE TEST ---
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
// ----------------------------------------------

bool canStart = false; 

void setup() {
    Serial.begin(115200);
    while (!Serial) { delay(100); }
    delay(2000); // Le temps de poser le robot
    Serial.println("\n--- DEMARRAGE TEST BLOQUANT ---");
    
    // TEST 1 : Avancer de 100 mm (10 cm)
    rollingBasis->moveForwardBlocking(100.0f);
    
    // TEST 2 : Tourner de 90 degrés (PI / 2 radians)
    // 1.5708 rad = 90°
    rollingBasis->turnBlocking(1.5708f);
    
    // TEST 3 : Ré-avancer de 100 mm
    rollingBasis->moveForwardBlocking(100.0f);
    
    Serial.println("\n--- FIN DES TESTS ---");
}

long lastTime = 0; 

void loop() {
    // Mise à jour vitale des moteurs à chaque boucle
    leftMotor->update();
    rightMotor->update();

    // Mise à jour de la logique de déplacement toutes les 2ms
    if (millis() - lastTime > 2 && canStart) {
        
        // On remplace strategy->strategie_update() par l'update de notre action simple
        testAction->update();
        lastTime = millis();

        // Vérifie si le robot est arrivé à destination
        if (testAction->isFinished()) {
            Serial.println("Test terminé : Le robot a parcouru ses 10 cm !");
            canStart = false; // On stoppe les mises à jour de l'action
        }
    }
}