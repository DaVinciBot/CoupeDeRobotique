#include <Arduino.h>
#include <com.h>

Com::Com(usb_serial_class* stream, uint32_t baudrate) 
{
    this->stream = stream;
    stream->begin(baudrate);

    for (uint16_t k = 0; k < 256; k++)
        this->buffer[k] = 0;
}

Com::Com(HardwareSerial *stream, uint32_t baudrate)
{
    this->stream = stream;
    stream->begin(baudrate);

    for (uint16_t k = 0; k < 256; k++)
        this->buffer[k] = 0;
}

byte Com::handle() 
{
    while(this->stream->available()) {
        byte data = this->stream->read();
        this->buffer[this->pointer++] = data;

        if(this->pointer < 5)
            continue;

        bool is_signature = true;
        for (int i = 0; i < 4 && is_signature; i++)
            is_signature = this->buffer[pointer - 1 - i] == this->signature[3 - i];
            
        if (!is_signature)
            continue;

        byte msg_size = this->buffer[pointer - 5];
        if(this->pointer >= msg_size + 5) {
            this->pointer = 0;
            return msg_size;
        } else {
            this->pointer = 0;
        }
    }
    return 0;
}

byte* Com::read_buffer() {
    return this->buffer;
}

void Com::send_msg(byte *msg, byte size)
{
    this->stream->write(msg, size);
    this->stream->write(size);
    this->stream->write(this->signature, 4);
    this->stream->flush();
}

 