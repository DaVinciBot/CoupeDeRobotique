#include <Adafruit_NeoPixel.h>

#include <Adafruit_NeoPixel.h>

#define LED_PIN 15   // Broche de données connectée au bandeau LED
#define NUM_LEDS 63 // Nombre total de LEDs dans le bandeau

#define BANDE_SIZE_E 9

#define BANDE_SIZE_O 11

#define MINI_SIZE_E 6
#define MINI_SIZE_O 5

#define CENTRAL_SIZE 12

#define GRANDE_SIZE 

Adafruit_NeoPixel strip = Adafruit_NeoPixel(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);


word se[BANDE_SIZE_E] = {0, 1, 2, 3, 4, 5, 6, 7, 8};
word ne[BANDE_SIZE_E] = {23, 22, 21, 20, 19, 18, 17, 16, 15};

word so[BANDE_SIZE_O] = {62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52};
word no[BANDE_SIZE_O] = {36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46};

word miniE[MINI_SIZE_E] = {9, 10, 11, 12, 13, 14};
word miniO[MINI_SIZE_O] = {47, 48, 49, 50, 51};

word bandeauCentral[CENTRAL_SIZE] = {24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35};


void setup() {
  pinMode(2, INPUT);
  strip.begin();
  strip.show(); // Éteindre toutes les LEDs au démarrage
}

void loop() {
  if(digitalRead(2)==1)
   {
    for (int i = 0; i < BANDE_SIZE_O; i++) {
    strip.setPixelColor(no[i], strip.Color(0, 255, 0));
    strip.setPixelColor(so[i], strip.Color(0, 255, 0));
    strip.setPixelColor(bandeauCentral[i], strip.Color(0, 255, 0));
    if(i < BANDE_SIZE_E)
    {
      strip.setPixelColor(ne[i], strip.Color(0, 255, 0));
      strip.setPixelColor(se[i], strip.Color(0, 255, 0));
    }
    if(i < MINI_SIZE_E)
    {
      strip.setPixelColor(miniE[i], strip.Color(0, 255, 0));
    }
    if(i > MINI_SIZE_E)
    {
      strip.setPixelColor(miniE[i-MINI_SIZE_E], strip.Color(0, 255, 0));
    }
    if(i < MINI_SIZE_O)
    {
      strip.setPixelColor(miniO[i], strip.Color(0, 255, 0));
    }
    if(i > MINI_SIZE_O)
    {
      strip.setPixelColor(miniO[i-MINI_SIZE_O - 1], strip.Color(0, 255, 0));
    }
    strip.show();
    delay(100);
   }
   for (int i = 0; i < BANDE_SIZE_O; i++) {
    strip.setPixelColor(no[i], strip.Color(0, 0, 0));
    strip.setPixelColor(so[i], strip.Color(0, 0, 0));
    strip.setPixelColor(bandeauCentral[i], strip.Color(0, 0, 0));
    if(i < BANDE_SIZE_E)
    {
      strip.setPixelColor(ne[i], strip.Color(0, 0, 0));
      strip.setPixelColor(se[i], strip.Color(0, 0, 0));
    }
    if(i < MINI_SIZE_E)
    {
      strip.setPixelColor(miniE[i], strip.Color(0, 0, 0));
    }
    if(i > MINI_SIZE_E)
    {
      strip.setPixelColor(miniE[i-MINI_SIZE_E], strip.Color(0, 0, 0));
    }
    if(i < MINI_SIZE_O)
    {
      strip.setPixelColor(miniO[i], strip.Color(0, 0, 0));
    }
    if(i > MINI_SIZE_O)
    {
      strip.setPixelColor(miniO[i-MINI_SIZE_O - 1], strip.Color(0, 0, 0));
    }
    strip.show();
    delay(100);
   }
  }

   if(digitalRead(4) == 1)
   {
    for(int i=0; i < CENTRAL_SIZE; i++)
    {
      strip.setPixelColor(bandeauCentral[i], strip.Color(255, 0, 0));
    }
    for(int i=0; i < BANDE_SIZE_E; i++)
    {
      strip.setPixelColor(ne[i], strip.Color(255, 0, 0));
      strip.setPixelColor(se[i], strip.Color(255, 0, 0)) ;    
    }
    for(int i=0; i < BANDE_SIZE_O; i++)
    {
      strip.setPixelColor(no[i], strip.Color(255, 0, 0));
      strip.setPixelColor(so[i], strip.Color(255, 0, 0));    
    }
    for(int i=0; i < MINI_SIZE_E; i++)
    {
      strip.setPixelColor(miniE[i], strip.Color(255, 0, 0));    
    }
    for(int i=0; i < MINI_SIZE_O; i++)
    {
      strip.setPixelColor(miniO[i], strip.Color(255, 0, 0));    
    }
    strip.show();
   }

   else
   {
    for(int i=0; i < CENTRAL_SIZE; i++)
    {
      strip.setPixelColor(bandeauCentral[i], strip.Color(0, 0, 0));
    }
    for(int i=0; i < BANDE_SIZE_E; i++)
    {
      strip.setPixelColor(ne[i], strip.Color(0, 0, 0));
      strip.setPixelColor(se[i], strip.Color(0, 0, 0)) ;    
    }
    for(int i=0; i < BANDE_SIZE_O; i++)
    {
      strip.setPixelColor(no[i], strip.Color(0, 0, 0));
      strip.setPixelColor(so[i], strip.Color(0, 0, 0));    
    }
    for(int i=0; i < MINI_SIZE_E; i++)
    {
      strip.setPixelColor(miniE[i], strip.Color(0, 0, 0));    
    }
    for(int i=0; i < MINI_SIZE_O; i++)
    {
      strip.setPixelColor(miniO[i], strip.Color(0, 0, 0));    
    }
    strip.show();
   }
}
  /*
  if(digitalRead(2)){
     // Allumer toutes les LEDs en rouge
      colorWipe(strip.Color(255, 0, 0), 50); // Rouge à pleine intensité
      delay(1000);                          // Attendre 1 seconde
    
      // Allumer toutes les LEDs en vert
      colorWipe(strip.Color(0, 255, 0), 50); // Vert à pleine intensité
      delay(1000);                          // Attendre 1 seconde
    
      // Allumer toutes les LEDs en bleu
      colorWipe(strip.Color(0, 0, 255), 50); // Bleu à pleine intensité
      delay(1000);                          // Attendre 1 seconde
  }
  else{
      colorWipe(strip.Color(0, 0, 0), 50); // Rouge à pleine intensité
  }*/


// Fonction pour allumer progressivement les LEDs avec une couleur spécifique
void colorWipe(uint32_t color, int wait) {
  for (int i = 0; i < strip.numPixels(); i++) {
    strip.setPixelColor(i, color);
    strip.show();
    delay(wait);
  }
}
