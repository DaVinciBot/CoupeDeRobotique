#include <Arduino.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>

// Comment the following line to disable debug mode
#define WS_COM_DEBUG

#define DEFAULT_SERIAL_BAUDRATE 115200
#define JSON_RESPONSE_SIZE 200


// Callback class to handle the function to call when a new value is received
class Callback
{
public:
    // Attributes
    String msg;
    void (*function)(String data);

    // Constructor
    Callback(const String &msg, void (*function)(String data));

    // Static Methods (to manage callback array and pointer)
    // Alloc memory to add a new channel to the pointer
    static Callback deep_copy(const Callback &callback_to_copy);
    static Callback *push_callback_to_array(Callback *old_ptr, const Callback &callback_to_push, unsigned short new_size);

    // Handle callbacks array
    static void handle_callback_array(Callback *callbacks_ptr, unsigned short nb_callbacks, const String &msg, String &data);
};


// Server_Manager class to manage the connection with the server
class Server_Manager
{
private:
    // WiFi
    const char *ssid;
    const char *password;

    // Server connection
    const char* server_ip;
    int server_port;
    const char* endpoint;
    // Username to connect to the server
    const char* username;

    // WiFi and WS client object
    WiFiClient wifi_client;
    WebSocketsClient ws_client;

    // WS event
    void ws_event(WStype_t type, uint8_t * payload, size_t length);

    // Callbacks array, it stores the subscribed msg and the function to call
    Callback *callbacks_ptr;
    unsigned short nb_callbacks = 0;

    // Tools
    String make_request(const String &msg, const String &data, bool use_millis_as_ts = true);
    void send_request(String request);

public:
    // Constructor
    Server_Manager(
        // WiFi
        const char *ssid,
        const char *password,
        // Server connection
        const char* server_ip,
        int server_port,
        const char* endpoint,
        // Username to connect to the server
        const char* username
    );

    // Initialize the server connection
    void begin();

    // Interact with the server
    void handle(uint16_t wait = 0);
    void add_callback(const String &msg, void (*function)(String data));
    void send(const String &msg, const String &data, bool use_millis_as_ts = true);
};


// Com class to manage the communication with the server, with only high-level methods
class Com 
{
private:
    // Server_Manager pointer, to interact with the server
    Server_Manager *server_ptr;

public:
    // Constructor
    Com(
        // WiFi
        const char *ssid,
        const char *password,
        // Server connection
        const char* server_ip,
        int server_port,
        const char* endpoint,
        // Username to connect to the server
        const char* username
    );

    // Initialize the server connection
    void begin();

    // Interact with the server
    void handle();
    void add_callback(const String &msg, void (*function)(String data));
    void send(const String &msg, const String &data, bool use_millis_as_ts = true);
};