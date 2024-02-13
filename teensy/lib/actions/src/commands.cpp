#include <commands.h>

// tries to call the functions called by the rasp and send back an error message otherwise
void handle_callback(Com *com)
{
    byte size = com->handle();
    if (size > 0)
    {
        byte *msg = com->read_buffer();

        if (msg[0] == PRESHOT)
        {
            // send the preshot message to the rasp
            msg_Preshot *preshot_msg = (msg_Preshot *)msg;
            // alloc the memory for the message
            byte *data = (byte *)malloc(preshot_msg->data_size);
            // copy the data from the message to the allocated memory
            memcpy(data, preshot_msg->data, preshot_msg->data_size);
            // save 
            free(data);
        }
        else if (functions[msg[0]] != 0) // verifies if the id of the function received by com is defined
        {
            functions[msg[0]](msg, size); // call the function by it's id and with the parameters received by com
        }
        else if (msg[0] == NACK)
        {
            // send again the message that wasn't received by the rasp
            com->send_msg((byte*)&com->last_msg->msg, com->last_msg->size, true);
        }
        else
        {
            // If message is unknown, inform the rasp 
            msg_Unknown_Msg_Type error_message;
            error_message.type_id = msg[0];
            com->send_msg((byte *)&error_message, sizeof(msg_Unknown_Msg_Type)); 
        }
    }
}


