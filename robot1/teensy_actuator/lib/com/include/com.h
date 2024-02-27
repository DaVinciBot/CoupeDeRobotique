#include <Arduino.h>

// Com class
class Com {

private:
    byte* buffer = new byte[256];
    byte signature[4] = {0xBA, 0xDD, 0x1C, 0xC5};
    byte pointer = 0;
    Stream* stream;
   
public:
    Com(usb_serial_class *stream, uint32_t baudrate);
    Com(HardwareSerial *stream, uint32_t baudrate);
    byte handle();
    byte * read_buffer();
    void send_msg(byte *msg, byte size);
};