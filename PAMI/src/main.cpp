// #include "OTA.h"
// AsyncWebServer server(80);
// CustomOTA ota("DVB_CDR", "davincibot", &server);
//#include <Arduino.h>
//#include <SPI.h>
//#include <RadioLib.h>
//#include <BaseLoRa.h>
//#include <SX126x.h>

#include <Arduino.h>
/*
  RadioLib SX126x Ping-Pong Example

  This example is intended to run on two SX126x radios,
  and send packets between the two.

  For default module settings, see the wiki page
  https://github.com/jgromes/RadioLib/wiki/Default-configuration#sx126x---lora-modem

  For full API reference, see the GitHub Pages
  https://jgromes.github.io/RadioLib/
*/
/*
// include the library
#include <RadioLib.h>
#include <BaseLoRa.h>

//#include <SX126x.h>
#include <SPI.h>

// uncomment the following only on one
// of the nodes to initiate the pings
//#define INITIATING_NODE

// SX1262 has the following connections:
// NSS pin:   10
// DIO1 pin:  2
// NRST pin:  3
// BUSY pin:  9
//SX1262 radio = new Module(10,2,3,9);

// or detect the pinout automatically using RadioBoards
// https://github.com/radiolib-org/RadioBoards

#define RADIO_BOARD_AUTO
#include <RadioBoards.h>
Radio radio = new RadioModule();


// save transmission states between loops
int transmissionState = RADIOLIB_ERR_NONE;

// flag to indicate transmission or reception state
bool transmitFlag = false;

// flag to indicate that a packet was sent or received
volatile bool operationDone = false;

// this function is called when a complete packet
// is transmitted or received by the module
// IMPORTANT: this function MUST be 'void' type
//            and MUST NOT have any arguments!
#if defined(ESP8266) || defined(ESP32)
  ICACHE_RAM_ATTR
#endif
void setFlag(void) {
  // we sent or received a packet, set the flag
  operationDone = true;
}

void setup() {
  Serial.begin(9600);

  // initialize SX1262 with default settings
  Serial.print(F("[SX1262] Initializing ... "));
  int state = radio.begin();
  if (state == RADIOLIB_ERR_NONE) {
    Serial.println(F("success!"));
  } else {
    Serial.print(F("failed, code "));
    Serial.println(state);
    //while (true) { delay(10); }
  }

  // set the function that will be called
  // when new packet is received
  radio.setDio1Action(setFlag);

  #if defined(INITIATING_NODE)
    // send the first packet on this node
    Serial.print(F("[SX1262] Sending first packet ... "));
    transmissionState = radio.startTransmit("Hello World!");
    transmitFlag = true;
  #else
    // start listening for LoRa packets on this node
    Serial.print(F("[SX1262] Starting to listen ... "));
    state = radio.startReceive();
    if (state == RADIOLIB_ERR_NONE) {
      Serial.println(F("success!"));
    } else {
      Serial.print(F("failed, code "));
      Serial.println(state);
      //while (true) { delay(10); }
    }
  #endif
}

void loop() {
  // check if the previous operation finished
  if(operationDone) {
    // reset flag
    operationDone = false;

    if(transmitFlag) {
      // the previous operation was transmission, listen for response
      // print the result
      if (transmissionState == RADIOLIB_ERR_NONE) {
        // packet was successfully sent
        Serial.println(F("transmission finished!"));

      } else {
        Serial.print(F("failed, code "));
        Serial.println(transmissionState);

      }

      // listen for response
      radio.startReceive();
      transmitFlag = false;

    } else {
      // the previous operation was reception
      // print data and send another packet
      String str;
      int state = radio.readData(str);

      if (state == RADIOLIB_ERR_NONE) {
        // packet was successfully received
        Serial.println(F("[SX1262] Received packet!"));

        // print data of the packet
        Serial.print(F("[SX1262] Data:\t\t"));
        Serial.println(str);

        // print RSSI (Received Signal Strength Indicator)
        Serial.print(F("[SX1262] RSSI:\t\t"));
        Serial.print(radio.getRSSI());
        Serial.println(F(" dBm"));

        // print SNR (Signal-to-Noise Ratio)
        Serial.print(F("[SX1262] SNR:\t\t"));
        Serial.print(radio.getSNR());
        Serial.println(F(" dB"));

      }

      // wait a second before transmitting again
      delay(1000);

      // send another one
      Serial.print(F("[SX1262] Sending another packet ... "));
      transmissionState = radio.startTransmit("Hello World!");
      transmitFlag = true;
    }
  
  }
}
*/
//  //#include <AnalogIn.h>
//  #include "mbed.h"
//  #include <RadioLib.h>
//  #include "sx126x-hal.h"
//  #include "sx126x.h"
//  //#include "debug.h"
  
//  #define SEND_PING_BEAT_US 200000
//  #define RX_TIMEOUT_US 200000
 
//  /* Set this flag to '1' to display debug messages on the console */
//  #define DEBUG_MESSAGE   1
  
//  /* Set this flag to '1' to use the LoRa modulation or to '0' to use FSK modulation */
//  #define USE_MODEM_LORA  1
//  #define USE_MODEM_FSK   !USE_MODEM_LORA
  
//  #define RF_FREQUENCY                                    868000000 // Hz
//  #define TX_OUTPUT_POWER                                 14        // 14 dBm
  
//  #if USE_MODEM_LORA == 1
  
//      #define LORA_BANDWIDTH                              LORA_BW_500         // [0: 125 kHz,
//                                                                    //  1: 250 kHz,
//                                                                    //  2: 500 kHz,
//                                                                    //  3: Reserved]
//      #define LORA_SPREADING_FACTOR                       LORA_SF7         // [SF7..SF12]
//      #define LORA_LOWDATARATEOPTIMIZE                    0
//      #define LORA_CODINGRATE                             LORA_CR_4_5         // [1: 4/5,
//                                                                    //  2: 4/6,
//                                                                    //  3: 4/7,
//                                                                    //  4: 4/8]
//      #define LORA_PREAMBLE_LENGTH                        8         // Same for Tx and Rx
//      #define LORA_SYMBOL_TIMEOUT                         5         // Symbols
//      #define LORA_HEADER_TYPE                            LORA_PACKET_VARIABLE_LENGTH
//      #define LORA_FHSS_ENABLED                           false  
//      #define LORA_NB_SYMB_HOP                            4     
//      #define LORA_IQ                                     LORA_IQ_NORMAL
//      #define LORA_CRC_MODE                               LORA_CRC_OFF
  
//  #elif USE_MODEM_FSK == 1
  
//      #define FSK_FDEV                                    25000     // Hz
//      #define FSK_DATARATE                                19200     // bps
//      #define FSK_BANDWIDTH                               RX_BW_93800     // Hz
//      #define FSK_MODULATION_SHAPPING                     MOD_SHAPING_G_BT_05
//      #define FSK_PREAMBLE_LENGTH                         5         // Same for Tx and Rx
//      #define FSK_HEADER_TYPE                             RADIO_PACKET_VARIABLE_LENGTH
//      #define FSK_CRC_MODE                                RADIO_CRC_2_BYTES_CCIT
//      #define FSK_ADDR_FILTERING                          RADIO_ADDRESSCOMP_FILT_NODE;
//      #define FSK_WHITENING_MODE                          RADIO_DC_FREE_OFF
//      #define FSK_PREAMBLE_DETECTOR_MODE                  RADIO_PREAMBLE_DETECTOR_OFF
//      #define FSK_SYNCWORD_LENGTH                         8
//  #else
//      #error "Please define a modem in the compiler options."
//  #endif
  
//  #define RX_TIMEOUT_VALUE                                3500      // in ms
//  #define BUFFER_SIZE                                     32        // Define the payload size here
  
//  #if( defined ( TARGET_KL25Z ) || defined ( TARGET_LPC11U6X ) )
//  DigitalOut led( LED2 );
//  #else
//  DigitalOut led( LED1 );
//  #endif
  
//   /*
//   * Callback functions prototypes
//   */
//  /*!
//   * @brief Function to be executed on Radio Tx Done event
//   */
//  void OnTxDone( void );
  
//  /*!
//   * @brief Function to be executed on Radio Rx Done event
//   */
//  void OnRxDone( void );
  
//  /*!
//   * @brief Function executed on Radio Tx Timeout event
//   */
//  void OnTxTimeout( void );
  
//  /*!
//   * @brief Function executed on Radio Rx Timeout event
//   */
//  void OnRxTimeout( void );
  
//  /*!
//   * @brief Function executed on Radio Rx Error event
//   */
//  void OnRxError( IrqErrorCode_t errCode );
  
//  /*!
//   * @brief Function executed on Radio Fhss Change Channel event
//   */
//  void OnFhssChangeChannel( uint8_t channelIndex );
 
//  typedef struct{
//      RadioPacketTypes_t packetType;
//      int8_t txPower;
//      RadioRampTimes_t txRampTime;
//      ModulationParams_t modParams;
//      PacketParams_t packetParams;
//      uint32_t rfFrequency;
//      uint16_t irqTx;
//      uint16_t irqRx;
//      uint32_t txTimeout;
//      uint32_t rxTimeout;
//  }RadioConfigurations_t;
//  RadioConfigurations_t radioConfiguration;
  
//  /*
//   *  Global variables declarations
//   */
//  typedef enum
//  {
//      SEND_PACKET,
//      WAIT_SEND_DONE,
//      RECEIVE_PACKET,
//      WAIT_RECEIVE_DONE,
//      PACKET_RECEIVED,
//  }AppStates_t;
//  volatile AppStates_t State = SEND_PACKET;
 
//  typedef struct{
//      bool rxDone;
//      bool rxError;
//      bool txDone;
//      bool rxTimeout;
//      bool txTimeout;
//  }RadioFlags_t;
//  RadioFlags_t radioFlags = {
//      .txDone = false,
//      .rxDone = false,
//      .rxError = false,
//      .rxTimeout = false,
//      .txTimeout = false,
//  };
  
//  /*!
//   * Radio events function pointer
//   */
//  static RadioCallbacks_t RadioEvents = {
//      .txDone = &OnTxDone,
//      .txTimeout = &OnTxTimeout,
//      .rxDone = &OnRxDone,
//      .rxPreambleDetect = NULL,
//      .rxHeaderDone = NULL,
//      .rxTimeout = &OnRxTimeout,
//      .rxError = &OnRxError,
//      .cadDone = NULL,
//  };
 
//  /*
//   *  Global variables declarations
//   */
//  //Radio Radio( NULL );
//  #define MESSAGE_SIZE 4
//  typedef uint8_t Messages_t[MESSAGE_SIZE];
//  const Messages_t PingMsg = {'P', 'I', 'N', 'G'};
//  const Messages_t PongMsg = {'P', 'O', 'N', 'G'};
//  const Messages_t *messageToReceive = &PongMsg;
//  const Messages_t *messageToSend = &PingMsg;
  
//  uint8_t BufferSize = BUFFER_SIZE;
//  uint8_t Buffer[BUFFER_SIZE];
  
//  int8_t RssiValue = 0;
//  int8_t SnrValue = 0;
 
//  void GetRssiSnr(int8_t *rssi, int8_t *snr);
//  SX126xHal Radio( D11, D12, D13, D7, D3, D5, NC, NC, A0, A1, A2, D8, &RadioEvents );
 
//  void SetToMaster(void);
//  void SetToSlave(void);
//  void RunMasterStateMachine();
//  void RunSlaveStateMachine();
//  void SetConfiguration(RadioConfigurations_t *config);
//  void ConfigureGeneralRadio(SX126xHal *radio, RadioConfigurations_t *config);
//  void ConfigureRadioTx(SX126xHal *radio, RadioConfigurations_t *config);
//  void ConfigureRadioRx(SX126xHal *radio, RadioConfigurations_t *config);
//  void PrepareBuffer(SX126xHal *radio, const Messages_t *messageToSend);
//  bool isMaster = true;
//  bool masterCanSend = true;
//  void MasterSendNextEvent(void){masterCanSend = true;}
//  bool slaveCanListen = false;
//  void SlaveListenNextEvent(void){slaveCanListen = true;}
//  Ticker masterSendNextTicker;
//  Ticker slaveListenNextTicker;
 
//  Serial serial(USBTX, USBRX);
 
//  int main( void ) 
//  {
//      Radio.Reset();
//      Radio.Init();
//      serial.baud(115200);
//      SetToMaster();
//      SetConfiguration(&radioConfiguration);
//      ConfigureGeneralRadio(&Radio, &radioConfiguration);
//      while(true){
//          if(isMaster){
//              RunMasterStateMachine();
//          }
//          else{
//              RunSlaveStateMachine();
//          }
//      }
//  }
 
//  void RunMasterStateMachine(){
//      switch(State){
//          case SEND_PACKET:{
//              if(masterCanSend == true){
//                  masterCanSend = false;
//                  masterSendNextTicker.attach_us(&MasterSendNextEvent, SEND_PING_BEAT_US);
//                  PrepareBuffer(&Radio, messageToSend);
//                  ConfigureRadioTx(&Radio, &radioConfiguration);
//                  Radio.SetTx(radioConfiguration.txTimeout);
//                  printf("Ping...\n");
//                  State = WAIT_SEND_DONE;
//              }
//              break;
//          }
         
//          case WAIT_SEND_DONE:{
//              if(radioFlags.txDone){
//                  radioFlags.txDone = false;
//                  State = RECEIVE_PACKET;
//              }
//              if(radioFlags.txTimeout){
//                  radioFlags.txTimeout = false;
//                  State = SEND_PACKET;
//              }
//              break;
//          }
         
//          case RECEIVE_PACKET:{
//              ConfigureRadioRx(&Radio, &radioConfiguration);
//              Radio.SetRx(radioConfiguration.rxTimeout);
//              State = WAIT_RECEIVE_DONE;
//              break;
//          }
         
//          case WAIT_RECEIVE_DONE:{
//              if(radioFlags.rxDone == true){
//                  radioFlags.rxDone = false;
//                  State = PACKET_RECEIVED;
//              }
//              if(radioFlags.rxTimeout == true){
//                  radioFlags.rxTimeout = false;
//                  State = SEND_PACKET;
//              }
//              break;
//          }
         
//          case PACKET_RECEIVED:{
//              Radio.GetPayload( Buffer, &BufferSize, BUFFER_SIZE );
//              RssiValue = Radio.GetRssiInst();
//              GetRssiSnr(&RssiValue, &SnrValue);
//              if( strncmp(( const char* )Buffer, (const char*)messageToReceive, MESSAGE_SIZE ) == 0 ){
//                  printf("...Pong\n");
//                  State = SEND_PACKET;
//              }
//              else if( strncmp(( const char* )Buffer, (const char*)messageToSend, MESSAGE_SIZE ) == 0 ){
//                  // Another Master is in the air, swith to slave
//                  SetToSlave();
//              }
//              else{
//                  printf("WRONG PAYLOAD\n");
//                  SetToMaster();
//              }
//              break;
//          }
//      }
//  }
 
//  void RunSlaveStateMachine(){
//      switch(State){
//          case RECEIVE_PACKET:{
//              if(slaveCanListen == true){
//                  slaveCanListen = false;
//                  ConfigureRadioRx(&Radio, &radioConfiguration);
//                  Radio.SetRx(radioConfiguration.rxTimeout);
//                  slaveListenNextTicker.attach_us(&SlaveListenNextEvent, SEND_PING_BEAT_US - ( RX_TIMEOUT_US>>1 ));
//                  State = WAIT_RECEIVE_DONE;
//              }
//              break;
//          }
         
//          case WAIT_RECEIVE_DONE:{
//              if(radioFlags.rxDone == true){
//                  radioFlags.rxDone = false;
//                  State = PACKET_RECEIVED;
//              }
//              if(radioFlags.rxTimeout == true){
//                  radioFlags.rxTimeout = false;
//                  SetToMaster();
//              }
//              break;
//          }
         
//          case PACKET_RECEIVED:{
//              Radio.GetPayload( Buffer, &BufferSize, BUFFER_SIZE );
//              RssiValue = Radio.GetRssiInst();
//              GetRssiSnr(&RssiValue, &SnrValue);
//              if( strncmp(( const char* )Buffer, (const char*)messageToReceive, MESSAGE_SIZE ) == 0 ){
//                  printf("...Ping\n");
//                  State = SEND_PACKET;
//              }
//              else{
//                  SetToMaster();
//              }
//              break;
//          }
         
//          case SEND_PACKET:{
//              PrepareBuffer(&Radio, messageToSend);
//              ConfigureRadioTx(&Radio, &radioConfiguration);
//              printf("Pong...\n");
//              Radio.SetTx(radioConfiguration.txTimeout);
//              State = WAIT_SEND_DONE;
//              break;
//          }
         
//          case WAIT_SEND_DONE:{
//              if(radioFlags.txDone){
//                  radioFlags.txDone = false;
//                  State = RECEIVE_PACKET;
//              }
//              if(radioFlags.txTimeout){
//                  radioFlags.txTimeout = false;
//                  SetToMaster();
//              }
//              break;
//          }
//      }
//  }
 
//  void SetToMaster(){
//      printf("-->Master\n");
//      isMaster = true;
//      masterCanSend = true;
//      State = SEND_PACKET;
//      messageToReceive = &PongMsg;
//      messageToSend = &PingMsg;
//  }
 
//  void SetToSlave(){
//      slaveCanListen = false;
//      slaveListenNextTicker.attach_us(&SlaveListenNextEvent, SEND_PING_BEAT_US - ( RX_TIMEOUT_US>>1 ));
//      printf("--> Slave\n");
//      isMaster = false;
//      State = RECEIVE_PACKET;
//      messageToReceive = &PingMsg;
//      messageToSend = &PongMsg;
//  }
  
//  void OnTxDone( void )
//  {
//      radioFlags.txDone = true;
//  }
  
//  void OnRxDone( void )
//  {
//      radioFlags.rxDone = true;
//  }
  
//  void OnTxTimeout( void )
//  {
//      radioFlags.txTimeout = true;
//      debug_if( DEBUG_MESSAGE, "> OnTxTimeout\n\r" );
//  }
  
//  void OnRxTimeout( void )
//  {
//      radioFlags.rxTimeout = true;
//      debug_if( DEBUG_MESSAGE, "> OnRxTimeout\n\r" );
//  }
  
//  void OnRxError( IrqErrorCode_t errCode )
//  {
//      radioFlags.rxError = true;
//      debug_if( DEBUG_MESSAGE, "> OnRxError\n\r" );
//  }
 
//  void SetConfiguration(RadioConfigurations_t *config){
//      config->irqRx = IRQ_RX_DONE | IRQ_RX_TX_TIMEOUT;
//      config->irqTx = IRQ_TX_DONE | IRQ_RX_TX_TIMEOUT;
//      config->rfFrequency = RF_FREQUENCY;
//      config->txTimeout = 0;
//      config->rxTimeout = (uint32_t)(RX_TIMEOUT_US / 15.625);
//      config->txPower = TX_OUTPUT_POWER;
//      config->txRampTime = RADIO_RAMP_200_US;
//      #if USE_MODEM_LORA == 1
//          config->packetType = PACKET_TYPE_LORA;
//          config->modParams.PacketType = PACKET_TYPE_LORA;
//          config->modParams.Params.LoRa.Bandwidth = LORA_BANDWIDTH;
//          config->modParams.Params.LoRa.CodingRate = LORA_CODINGRATE;
//          config->modParams.Params.LoRa.LowDatarateOptimize = LORA_LOWDATARATEOPTIMIZE;
//          config->modParams.Params.LoRa.SpreadingFactor = LORA_SPREADING_FACTOR;
//          config->packetParams.PacketType = PACKET_TYPE_LORA;
//          config->packetParams.Params.LoRa.CrcMode = LORA_CRC_MODE;
//          config->packetParams.Params.LoRa.HeaderType = LORA_HEADER_TYPE;
//          config->packetParams.Params.LoRa.InvertIQ = LORA_IQ;
//          config->packetParams.Params.LoRa.PayloadLength = BUFFER_SIZE;
//          config->packetParams.Params.LoRa.PreambleLength = LORA_PREAMBLE_LENGTH;
//      #elif USE_MODEM_FSK == 1
//          config->packetType = PACKET_TYPE_GFSK;
//          config->modParams.PacketType = PACKET_TYPE_GFSK;
//          config->modParams.Params.Gfsk.Bandwidth = FSK_BANDWIDTH;
//          config->modParams.Params.Gfsk.BitRate = 1024000000 / FSK_DATARATE;
//          config->modParams.Params.Gfsk.Fdev = FSK_FDEV * 1.048576;
//          config->modParams.Params.Gfsk.ModulationShaping = FSK_MODULATION_SHAPPING;
//          config->packetParams.PacketType = PACKET_TYPE_GFSK;
//          config->packetParams.Params.Gfsk.AddrComp = FSK_ADDR_FILTERING;
//          config->packetParams.Params.Gfsk.CrcLength = FSK_CRC_MODE;
//          config->packetParams.Params.Gfsk.DcFree = FSK_WHITENING_MODE;
//          config->packetParams.Params.Gfsk.HeaderType = FSK_HEADER_TYPE;
//          config->packetParams.Params.Gfsk.PayloadLength = BUFFER_SIZE;
//          config->packetParams.Params.Gfsk.PreambleLength = FSK_PREAMBLE_LENGTH;
//          config->packetParams.Params.Gfsk.PreambleMinDetect = FSK_PREAMBLE_DETECTOR_MODE;
//          config->packetParams.Params.Gfsk.SyncWordLength = FSK_SYNCWORD_LENGTH;
//      #endif
//  }
 
//  void ConfigureGeneralRadio(SX126xHal *radio, RadioConfigurations_t *config){
//      radio->SetPacketType(config->packetType);
//      radio->SetPacketParams(&config->packetParams);
//      radio->SetModulationParams(&config->modParams);
//      radio->SetRfFrequency(config->rfFrequency);
//      radio->SetTxParams(config->txPower, config->txRampTime);
//      radio->SetInterruptMode();
//      if(config->packetType == PACKET_TYPE_GFSK){
//          uint8_t syncword[8] = {0xF0, 0x0F, 0x55, 0xAA, 0xF0, 0x0F, 0x55, 0xAA};
//          radio->SetSyncWord(syncword);
//      }
//  }
 
//  void ConfigureRadioTx(SX126xHal *radio, RadioConfigurations_t *config){
//      radio->SetDioIrqParams(config->irqTx, config->irqTx, IRQ_RADIO_NONE, IRQ_RADIO_NONE);
//  }
 
//  void ConfigureRadioRx(SX126xHal *radio, RadioConfigurations_t *config){
//      radio->SetDioIrqParams(config->irqRx, config->irqRx, IRQ_RADIO_NONE, IRQ_RADIO_NONE);
//  }
 
//  void PrepareBuffer(SX126xHal *radio, const Messages_t *messageToSend){
//      radio->SetPayload((uint8_t*)messageToSend, MESSAGE_SIZE);
//  }
 
//  void GetRssiSnr(int8_t *rssi, int8_t *snr)
//  {
//      PacketStatus_t pkt_stat;
//      Radio.GetPacketStatus(&pkt_stat);    
//      #if USE_MODEM_LORA == 1
//          *rssi = pkt_stat.Params.LoRa.RssiPkt;
//          *snr = pkt_stat.Params.LoRa.SnrPkt;
//      #else
//          *rssi = pkt_stat.Params.Gfsk.RssiSync;
//      #endif
//  }
 
/*
#include <SPI.h>

void setup() {
  Serial.begin(115200);
  //while (!Serial);

  SPI.begin(); // Initialisation du bus SPI
  Serial.println("Test SPI en mode loopback.");

  // Envoyer une donnée en loopback (MOSI connecté à MISO)
  byte dataOut = 0x55; // Valeur test
  byte dataIn = SPI.transfer(dataOut);
  
  Serial.print("Donnée envoyée : 0x");
  Serial.print(dataOut, HEX);
  Serial.print(" - Donnée reçue : 0x");
  Serial.println(dataIn, HEX);

  if (dataOut == dataIn) {
    Serial.println("Test SPI réussi !");
  } else {
    Serial.println("Test SPI échoué !");
  }
}

void loop() {}
*/

/*
#include <RadioLib.h>

// Mapping des broches selon XIAO_ESP32S3_Sense_Pinout.xlsx
#define LORA_NSS_PIN   10    // Chip Select (NSS)
#define LORA_DIO1_PIN  11    // Broche d'interruption (DIO1)
#define LORA_RST_PIN   12    // Broche de réinitialisation (NRST)
#define LORA_BUSY_PIN  13    // Broche d'état (BUSY)

// Création de l'instance du module SX1262
SX1262 lora = new Module(LORA_NSS_PIN, LORA_DIO1_PIN, LORA_RST_PIN, LORA_BUSY_PIN);

void setup() {
  Serial.begin(115200);
  //while(!Serial);
  Serial.println("LoRa TX - Initialisation du module...");

  // Initialisation du module sur 868 MHz (à adapter selon votre région)
  int state = lora.begin(868.0);
  if(state == RADIOLIB_ERR_NONE) {
    Serial.println("Module LoRa initialisé avec succès !");
  } else {
    Serial.print("Erreur d'initialisation, code : ");
    Serial.println(state);
    //while(true);
  }
}

void loop() {
  String message = "Bonjour, c'est un test LoRa TX !";
  Serial.print("Envoi du message : ");
  Serial.println(message);
  
  int state = lora.transmit(message);
  if(state == RADIOLIB_ERR_NONE) {
    Serial.println("Message envoyé !");
  } else {
    Serial.print("Erreur d'envoi, code : ");
    Serial.println(state);
  }
  
  delay(5000); // Pause de 5 secondes entre chaque transmission
}

*/
/*
#include <Arduino.h>
#include <SPI.h>
#include <BaseLoRa.h>
#include <SX126x.h>

SX126x LoRa;

// Message à transmettre
char message[] = "HeLoRa World!";
uint8_t nBytes = sizeof(message);
uint8_t counter = 0;

void setup() {
  Serial.begin(38400);
  
  // Initialisation du module LoRa avec les pins définies
  int8_t nssPin = 10, resetPin = 9, busyPin = 4, irqPin = -1, txenPin = 8, rxenPin = 7;
  if (!LoRa.begin(nssPin, resetPin, busyPin, irqPin, txenPin, rxenPin)) {
    Serial.println("Erreur d'initialisation de la radio LoRa");
    //while (1);
  }
  
  // Configuration de la fréquence, puissance, modulation et paquet
  LoRa.setFrequency(915000000);
  LoRa.setTxPower(17, SX126X_TX_POWER_SX1262);
  uint8_t sf = 7;
  uint32_t bw = 125000;
  uint8_t cr = 5;
  LoRa.setLoRaModulation(sf, bw, cr);
  
  uint8_t headerType = SX126X_HEADER_EXPLICIT;
  uint16_t preambleLength = 12;
  uint8_t payloadLength = 15;  // 14 octets pour le message + 1 octet pour le compteur
  bool crcType = true;
  LoRa.setLoRaPacket(headerType, preambleLength, payloadLength, crcType);
  
  LoRa.setSyncWord(0x3444);
  
  Serial.println("Transmetteur LoRa initialisé");
}

void loop() {
  // Préparer et envoyer le paquet (message + compteur)
  LoRa.beginPacket();
  LoRa.write(message, nBytes);
  LoRa.write(counter);
  LoRa.endPacket();
  
  // Affichage sur le moniteur série
  Serial.print("Transmitted: ");
  Serial.print(message);
  Serial.print("  ");
  Serial.println(counter++);
  
  Serial.print("Transmit time: ");
  Serial.print(LoRa.transmitTime());
  Serial.println(" ms");
  
  delay(1000);  // Délai entre chaque transmission
}
*/

/*
#include <Arduino.h>
#include <SPI.h>
#include <BaseLoRa.h>
#include <SX126x.h>

SX126x LoRa;

void setup() {
  Serial.begin(38400);
  
  // Initialisation du module LoRa avec les pins définies
  int8_t nssPin = 10, resetPin = 9, busyPin = 4, irqPin = -1, txenPin = 8, rxenPin = 7;
  if (!LoRa.begin(nssPin, resetPin, busyPin, irqPin, txenPin, rxenPin)) {
    Serial.println("Erreur d'initialisation de la radio LoRa");
  }
  
  // Configuration de la fréquence, puissance, modulation et paquet
  LoRa.setFrequency(915000000);
  LoRa.setTxPower(17, SX126X_TX_POWER_SX1262);
  uint8_t sf = 7;
  uint32_t bw = 125000;
  uint8_t cr = 5;
  LoRa.setLoRaModulation(sf, bw, cr);
  
  uint8_t headerType = SX126X_HEADER_EXPLICIT;
  uint16_t preambleLength = 12;
  uint8_t payloadLength = 15;  // 14 octets pour le message + 1 octet pour le compteur
  bool crcType = true;
  LoRa.setLoRaPacket(headerType, preambleLength, payloadLength, crcType);
  
  LoRa.setSyncWord(0x3444);
  
  Serial.println("Récepteur LoRa initialisé");
}

void loop() {
  // Passage en mode réception
  LoRa.request();
  LoRa.wait();
  
  // Vérification qu'il y a au moins un octet (le message + le compteur)
  if (LoRa.available() > 0) {
    // Le dernier octet est supposé être le compteur, on calcule donc la longueur du message
    const uint8_t msgLen = LoRa.available() - 1;
    if (msgLen > 0) {
      char receivedMessage[msgLen + 1];  // +1 pour le caractère nul de fin
      uint8_t receivedCounter;
      uint8_t i = 0;
      
      // Lecture de tous les octets sauf le dernier
      while (LoRa.available() > 1) {
        receivedMessage[i++] = LoRa.read();
      }
      
      // Terminer la chaîne
      receivedMessage[i] = '\0';
      
      // Lecture du dernier octet (le compteur)
      receivedCounter = LoRa.read();
      
      // Affichage du message et du compteur
      Serial.print("Received: ");
      Serial.print(receivedMessage);
      Serial.print("  ");
      Serial.println(receivedCounter);
      
      // Affichage des informations de signal
      Serial.print("Packet status: RSSI = ");
      Serial.print(LoRa.packetRssi());
      Serial.print(" dBm | SNR = ");
      Serial.print(LoRa.snr());
      Serial.println(" dB");
      
      // Vérification d'éventuelles erreurs
      uint8_t status = LoRa.status();
      if (status == SX126X_STATUS_CRC_ERR) {
        Serial.println("CRC error");
      } else if (status == SX126X_STATUS_HEADER_ERR) {
        Serial.println("Packet header error");
      }
    }
  }
  
  delay(1000);  // Délai avant la prochaine tentative de réception
}

*/
/*
#define NSS 3
#define NRESET 2
#define DIO1 0
#define BUSY 1
#define TX_POWER 13
#define SCK 8
#define MISO 9
#define MOSI 10

SX126x LoRa = new Module(NSS, DIO1, NRESET, BUSY);
//SX1262 LoRa = new Module(NSS,NRESET, BUSY);

void setup()
{

    Serial.begin(115200);
    while (!Serial);

    Serial.println("Initialisation du SPI...");
    SPI.begin(SCK, MISO, MOSI,NSS);
    // SPI.begin();  // SCK, MISO, MOSI, et SS
    delay(100);

    Serial.println("Initialisation du module LoRa SX1262...");
    int state = LoRa.begin();
    if (state == RADIOLIB_ERR_NONE)
    {
        Serial.println("Module SX1262 initialisé avec succès!");
    }
    else
    {
        Serial.print("Échec de l'initialisation du module SX1262. Code_ok_erreur : ");
        Serial.println(state);
        // while (true);
    }
    // ota.begin();
    // server.begin();
}

void loop()
{
    // ota.loop();

    Serial.println("Envoi du message : Hello, LoRa!");
    int state = LoRa.transmit("Hello, LoRa!");
    if (state == RADIOLIB_ERR_NONE)
    {
        Serial.println("Message envoyé avec succès!");
    }
    else
    {
        Serial.print("Échec de l'envoi du message. Code erreur: ");
        Serial.println(state);
    }
    delay(2000);

    Serial.println("Passage en mode réception...");
    String message;
    state = LoRa.receive(message);
    if (state == RADIOLIB_ERR_NONE)
    {
        Serial.print("Message reçu : ");
        Serial.println(message);
    }
    else
    {
        Serial.println("Aucun message reçu.");
    }
    delay(5000);
}
*/

#include <Arduino.h>
#include <SPI.h>
#include <BaseLoRa.h>
#include <SX126x.h>

SX126x LoRa;

// Message à transmettre
char message[] = "zzz"; // "ggg" correspond à 4 octets avec le '\0'
uint8_t counter = 0;

void setup() {
  // Démarrage de la communication série
  Serial.begin(38400);
  
  Serial.println("Begin LoRa radio");
  // Initialisation du module LoRa avec les broches définies
  int8_t nssPin = 10, resetPin = 9, busyPin = 4, irqPin = -1, txenPin = 8, rxenPin = 7;
  if (!LoRa.begin(nssPin, resetPin, busyPin, irqPin, txenPin, rxenPin)) {
    Serial.println("Something wrong, can't begin LoRa radio");
    //while (1);
  }
  
  // Configuration de la fréquence à 915 MHz (à adapter selon la réglementation locale)
  Serial.println("Set frequency to 915 MHz");
  LoRa.setFrequency(915000000);
  
  // Configuration de la puissance TX à +17 dBm
  Serial.println("Set TX power to +17 dBm");
  LoRa.setTxPower(17, SX126X_TX_POWER_SX1262);
  
  // Configuration des paramètres de modulation
  Serial.println("Set modulation parameters:\n\tSpreading factor = 7\n\tBandwidth = 125 kHz\n\tCoding rate = 4/5");
  uint8_t sf = 7;           // Facteur d'étalement
  uint32_t bw = 125000;     // Bande passante de 125 kHz
  uint8_t cr = 5;           // Coding rate 4/5
  LoRa.setLoRaModulation(sf, bw, cr);
  
  // Configuration des paramètres de paquet
  // Le payload doit correspondre exactement au nombre d'octets transmis :
  // message ("ggg" avec le '\0' = 4 octets) + compteur (1 octet) = 5 octets
  uint8_t headerType = SX126X_HEADER_EXPLICIT;  // Mode explicit
  uint16_t preambleLength = 12;                 // Longueur du préambule
  uint8_t payloadLength = 5;                    // Ajusté à 5 octets
  bool crcType = true;                          // Activation du CRC
  Serial.println("Set packet parameters:\n\tExplicit header type\n\tPreamble length = 12\n\tPayload Length = 5\n\tCRC on");
  LoRa.setLoRaPacket(headerType, preambleLength, payloadLength, crcType);
  
  // Configuration du mot de synchronisation (sync word)
  Serial.println("Set synchronize word to 0x3444");
  LoRa.setSyncWord(0x3444);
  
  Serial.println("\n-- LORA TRANSMITTER / RECEIVER --\n");
}

void loop() {
  
  
  // ---- MODE TRANSMISSION ----
  // Préparation et envoi du paquet LoRa (message + compteur)
  LoRa.beginPacket();
  // Envoi du message. sizeof(message) retourne 4 octets (les 3 caractères et le '\0')
  LoRa.write(message, sizeof(message));
  LoRa.write(counter);
  LoRa.endPacket();
  
  // Affichage du message transmis et incrémentation du compteur
  Serial.println();
  Serial.println();
  Serial.print("Transmitting: ");
  Serial.print(message);
  Serial.print("  ");
  Serial.println(counter++);
  
  // Attendre la fin de la transmission et afficher le temps d'émission
  LoRa.wait();
  Serial.print("Transmit time: ");
  Serial.print(LoRa.transmitTime());
  Serial.println(" ms");
  // ---- MODE RÉCEPTION ----
  // Demande de réception d'un nouveau paquet LoRa
  LoRa.request();
  // Attendre l'arrivée du paquet
  LoRa.wait();
  
  // Vérifier si un paquet a été reçu
  if (LoRa.available() > 0) {
    String receivedMessage = "";
    
    // Lire tous les octets sauf le dernier (celui-ci contient le compteur)
    while (LoRa.available() > 1) {
      receivedMessage += (char)LoRa.read();
    }
    
    // Lecture du dernier octet (compteur)
    uint8_t receivedCounter = LoRa.read();
    
    // Affichage du message reçu et du compteur
    Serial.print("Received: ");
    Serial.print(receivedMessage);
    Serial.print("  ");
    Serial.println(receivedCounter);
    
    // Affichage des informations de signal (RSSI et SNR)
    Serial.print("Packet status: RSSI = ");
    Serial.print(LoRa.packetRssi());
    Serial.print(" dBm | SNR = ");
    Serial.print(LoRa.snr());
    Serial.println(" dB");
    
    // Vérification d'éventuelles erreurs (CRC ou header)
    uint8_t status = LoRa.status();
    if (status == SX126X_STATUS_CRC_ERR) {
      Serial.println("CRC error");
    } else if (status == SX126X_STATUS_HEADER_ERR) {
      Serial.println("Packet header error");
    }
  } else {
    // Aucun paquet reçu
    Serial.println("No packet received");
  }
  // Délai avant la prochaine itération (ajustez si nécessaire)
  delay(500);
}



/*

#include <Arduino.h>
#include <SPI.h>
#include <BaseLoRa.h>
#include <SX126x.h>

SX126x LoRa;

// Message à transmettre
char message[] = "ggg";
uint8_t nBytes = sizeof(message);
uint8_t counter = 0;

void setup() {
  // Démarrage de la communication série
  Serial.begin(38400);
  
  Serial.println("Begin LoRa radio");
  // Initialisation du module LoRa avec les broches définies
  int8_t nssPin = 10, resetPin = 9, busyPin = 4, irqPin = -1, txenPin = 8, rxenPin = 7;
  if (!LoRa.begin(nssPin, resetPin, busyPin, irqPin, txenPin, rxenPin)) {
    Serial.println("Something wrong, can't begin LoRa radio");
    while (1);
  }
  
  // Configuration de la fréquence à 915 MHz (à adapter selon la réglementation locale)
  Serial.println("Set frequency to 915 MHz");
  LoRa.setFrequency(915000000);
  
  // Configuration de la puissance TX à +17 dBm
  Serial.println("Set TX power to +17 dBm");
  LoRa.setTxPower(17, SX126X_TX_POWER_SX1262);
  
  // Configuration des paramètres de modulation
  Serial.println("Set modulation parameters:\n\tSpreading factor = 7\n\tBandwidth = 125 kHz\n\tCoding rate = 4/5");
  uint8_t sf = 7;           // Facteur d'étalement
  uint32_t bw = 125000;     // Bande passante de 125 kHz
  uint8_t cr = 5;           // Coding rate 4/5
  LoRa.setLoRaModulation(sf, bw, cr);
  
  // Configuration des paramètres de paquet
  Serial.println("Set packet parameters:\n\tExplicit header type\n\tPreamble length = 12\n\tPayload Length = 15\n\tCRC on");
  uint8_t headerType = SX126X_HEADER_EXPLICIT;  // Mode explicit
  uint16_t preambleLength = 12;                 // Longueur du préambule
  uint8_t payloadLength = 15;                   // Longueur du payload (message + compteur)
  bool crcType = true;                          // Activation du CRC
  LoRa.setLoRaPacket(headerType, preambleLength, payloadLength, crcType);
  
  // Configuration du mot de synchronisation (sync word)
  Serial.println("Set synchronize word to 0x3444");
  LoRa.setSyncWord(0x3444);
  
  Serial.println("\n-- LORA TRANSMITTER / RECEIVER --\n");
}

void loop() {
  
  
  // ---- MODE RÉCEPTION ----
  // Demande de réception d'un nouveau paquet LoRa
  LoRa.request();
  // Attendre l'arrivée du paquet
  LoRa.wait();
  
  // Conversion des octets reçus en String
  if (LoRa.available() > 0) {
    String receivedMessage = "";
    
    // Lire tous les octets sauf le dernier (celui-ci contient le compteur)
    while (LoRa.available() > 1) {
      receivedMessage += (char)LoRa.read();
    }
    
    // Lecture du dernier octet (compteur)
    uint8_t receivedCounter = LoRa.read();
    
    // Affichage du message reçu et du compteur
    Serial.print("Received: ");
    Serial.print(receivedMessage);
    Serial.print("  ");
    Serial.println(receivedCounter);
    
    // Affichage des informations de signal (RSSI et SNR)
    Serial.print("Packet status: RSSI = ");
    Serial.print(LoRa.packetRssi());
    Serial.print(" dBm | SNR = ");
    Serial.print(LoRa.snr());
    Serial.println(" dB");
    
    // Vérification d'éventuelles erreurs (CRC ou header)
    uint8_t status = LoRa.status();
    if (status == SX126X_STATUS_CRC_ERR) {
      Serial.println("CRC error");
    } else if (status == SX126X_STATUS_HEADER_ERR) {
      Serial.println("Packet header error");
    }
  }
  // ---- MODE TRANSMISSION ----
  // Préparation et envoi du paquet LoRa (message + compteur)
  LoRa.beginPacket();
  LoRa.write(message, nBytes);
  LoRa.write(counter);
  LoRa.endPacket();
  
  // Affichage du message transmis et incrémentation du compteur
  Serial.println();
  Serial.println();
  Serial.print("Transmitting: ");
  Serial.print(message);
  Serial.print("  ");
  Serial.println(counter++);
  
  // Attendre la fin de la transmission et afficher le temps d'émission
  LoRa.wait();
  Serial.print("Transmit time: ");
  Serial.print(LoRa.transmitTime());
  Serial.println(" ms");
  
  // Délai avant la prochaine itération (ajustez si nécessaire)
  delay(500);
}

*/