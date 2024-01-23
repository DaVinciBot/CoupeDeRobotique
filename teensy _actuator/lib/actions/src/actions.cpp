#include <actions.h>
// tries to call the functions called by the rasp and send back an error message otherwise
void handle_callback(Com *com)
{
    byte size = com->handle();
    if (size > 0)
    {
        byte *msg = com->read_buffer();

        if (functions[msg[0]] != 0) // verifies if the id of the function received by com is defined
        {
            functions[msg[0]](msg, size); // call the function by it's id and with the parameters received by com
        }    
        else
        {
            msg_Unknown_Msg_Type error_message;
            error_message.type_id = msg[0];
            com->send_msg((byte *)&error_message, sizeof(msg_Unknown_Msg_Type)); // raise an error by sending 255 to the rasp if it tries to send a message that isn't defined by the teensy
        }
    }
}

/// @brief if the given servo exists this function enables to write the given angle on it  
/// @param servo a pointer to an instance of Servo_Motor
/// @param angle the angle to write of the servo
void servo_go_to(Servo* servo, int angle)
{
    servo->write(angle);
}
