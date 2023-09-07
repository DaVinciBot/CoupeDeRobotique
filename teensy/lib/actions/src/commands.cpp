#include <commands.h>

void handle_callback(Com *com)
{
    byte size = com->handle();
    if (size > 0)
    {
        byte *msg = com->read_buffer();

        if (functions[msg[0]] != 0)
            functions[msg[0]](msg + 1, size - 1);
    }
}