#include "com.h"


#pragma region Callback
// Constructor
Callback::Callback(const String &msg, void (*function)(String data))
{
    this->msg = msg;
    this->function = function;
}

// Static: Method(s)
Callback Callback::deep_copy(const Callback &callback_to_copy)
{
    // Create a new Callback object with the same attributes
    return Callback(callback_to_copy.msg, callback_to_copy.function);
}

Callback *Callback::push_callback_to_array(Callback *old_ptr, const Callback &callback_to_push, unsigned short new_size)
{
    Callback *new_ptr;

    // If no element in the array
    if (new_size - 1 == 0)
        new_ptr = (Callback *)calloc(new_size, sizeof(Callback));
    else
    {
        new_ptr = (Callback *)calloc(new_size, sizeof(Callback));
        for (unsigned short k = 0; k < new_size - 1; k++)
            new_ptr[k] = Callback::deep_copy(old_ptr[k]);

        free(old_ptr);
    }

    // Add the new channel to the new_ptr
    new_ptr[new_size - 1] = Callback::deep_copy(callback_to_push);

    return new_ptr;
}

void Callback::handle_callback_array(Callback *callback_ptr, unsigned short nb_callbacks, const String &msg, String &data)
{
    for (unsigned short k = 0; k < nb_callbacks; k++)
    {
        if (callback_ptr[k].msg == msg)
            callback_ptr[k].function(data);     
    }
} 
#pragma endregion


#pragma Server_Manager
// Constructor
Server_Manager::Server_Manager (
    // WiFi
    const char *ssid,
    const char *password,
    // Server connection
    const char* server_ip,
    int server_port,
    const char* endpoint,
    // Username to connect to the server
    const char* username
)
{
    // WiFi
    this->ssid = ssid;
    this->password = password;
    // Server connection
    this->server_ip = server_ip;
    this->server_port = server_port;
    this->endpoint = endpoint;
    // Username to connect to the server
    this->username = username;
}

// Private method(s)
// This method is called when a new event is received from the server through the WebSocket (connection, disconnection, new message)
void Server_Manager::ws_event(WStype_t type, uint8_t * payload, size_t length)
{
    // Handle the event
    switch (type) {
        case WStype_DISCONNECTED:
            #ifdef WS_COM_DEBUG    
                Serial.printf("[WebSocket] Disconnected!\n");
            #endif     
            break;

        case WStype_CONNECTED:
            #ifdef WS_COM_DEBUG    
                Serial.printf("[WebSocket] Connected!\n");
            #endif  
            break;

        case WStype_TEXT:
            #ifdef WS_COM_DEBUG    
                Serial.printf("[WebSocket] New message: %s\n", payload);
            #endif  
            
            // Deserialize the message to get the type
            StaticJsonDocument<JSON_RESPONSE_SIZE> json_message;     
            DeserializationError error = deserializeJson(json_message, String((char *)payload));

            // Handle deserialization error
            #ifdef WS_COM_DEBUG 
                if (error) {
                  Serial.print("deserializeJson() failed: ");
                  Serial.println(error.c_str());
                  break;
                } 
            #endif  

            /*
            Decode the incoming message according to this format:
            {
               "sender": str,
               "msg": str,
               "data": any,
               "ts": int  (Optionnal)
            }
            */

            // Check we receive a valid message (sender, msg, data)
            if (json_message.containsKey("sender") && json_message.containsKey("msg") && json_message.containsKey("data")) 
            {
                // Get the msg and data from the message
                String msg = json_message["msg"];
                String data = json_message["data"];

                // Handle the message: if a callback is registered for this message, call its associated function
                Callback::handle_callback_array(this->callbacks_ptr, this->nb_callbacks, msg, data);
            }
            else
            {
              #ifdef WS_COM_DEBUG 
                Serial.print("Unvalid message received !");
              #endif  
            }

            break;    
    }
}

// This method is used to create a request to send to the server, following the correct message format
String Server_Manager::make_request(const String &msg, const String &data, bool use_millis_as_ts)
{
    String request = "{\"sender\": \"" + String(this->username) + "\",";
    request += "\"msg\": \""+msg+"\",";
    request += "\"data\": \""+data+"\",";
    if (use_millis_as_ts)
      request += "\"ts\": "+ String(millis()) +"}";
    else
      request += "\"ts\": -1}";
    return request;
}

// This mehod is used to send a string to the server. This string must be a valid message !
// This method should not be used directly, prefer using the make_request() method to prepare the message before
void Server_Manager::send_request(String request)
{
    #ifdef WS_COM_DEBUG    
      Serial.print("New Request: ");
      Serial.println(request);
    #endif  
    this->ws_client.sendTXT(request);
}

// Public method(s)
// This method is used to initialize the connection to the WiFi, then with the server
void Server_Manager::begin()
{
    // Connect to WiFi
    #ifdef WS_COM_DEBUG    
        Serial.println();
        Serial.print("Connecting to ");
        Serial.println(this->ssid);
    #endif  
    WiFi.begin(this->ssid, this->password);

    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        #ifdef WS_COM_DEBUG    
            Serial.print(".");
        #endif  
    }

    #ifdef WS_COM_DEBUG    
        Serial.println("");
        Serial.println("WiFi connected");
        Serial.println("IP address: ");
        Serial.println(WiFi.localIP());
    #endif  

    // Connect to WS
    this->ws_client.begin(this->server_ip, this->server_port, this->endpoint + String("?sender=") + this->username);
    this->ws_client.onEvent([this](WStype_t type, uint8_t * payload, size_t length) {
        this->ws_event(type, payload, length);
    });
    this->ws_client.setReconnectInterval(5000);
}

// This method is used to handle the connection with the server, check if new messages are received, and call the associated callback
void Server_Manager::handle(uint16_t wait)
{
    this->ws_client.loop();
    delay(wait);
}

// This metho is used to add a callback on a specific message. 
// When this message is received, the associated function will be called with the message's data as parameter
void Server_Manager::add_callback(const String &msg, void (*function)(String data))
{
    this->nb_callbacks++;
    this->callbacks_ptr = Callback::push_callback_to_array(
        this->callbacks_ptr,
        Callback(msg, (*function)),
        this->nb_callbacks
    );
}

// This method is used to send a message to the server, it will create the message following the correct format before sending it
void Server_Manager::send(const String &msg, const String &data, bool use_millis_as_ts)
{
    this->send_request(
        this->make_request(msg, data, use_millis_as_ts)
    );
}
#pragma endregion


#pragma Com
// Constructor
Com::Com
(
    // WiFi
    const char *ssid,
    const char *password,
    // Server connection
    const char* server_ip,
    int server_port,
    const char* endpoint,
    // Username to connect to the server
    const char* username
)
{
    this->server_ptr = new Server_Manager(
        // WiFi
        ssid,
        password,
        // Server connection
        server_ip,
        server_port,
        endpoint,
        // Username to connect to the server
        username
    );
}

// Public method(s)
void Com::begin()
{
    // Initialize Serial if not already done (for debug)
    #ifdef WS_COM_DEBUG  
        if (!Serial)  
            Serial.begin(DEFAULT_SERIAL_BAUDRATE);
    #endif  

    // Initialize server connection (WiFi then WebSocket server)
    this->server_ptr->begin();
}

// This method is used to handle the connection with the server, check if new messages are received, and call the associated callback
void Com::handle()
{
    this->server_ptr->handle();
}

// This method is used to add a callback on a specific message.
void Com::add_callback(const String &msg, void (*function)(String data))
{
    this->server_ptr->add_callback(msg, function);
}

// This method is used to send a message to the server
void Com::send(const String &msg, const String &data, bool use_millis_as_ts)
{
    this->server_ptr->send(msg, data, use_millis_as_ts);
}
#pragma endregion










