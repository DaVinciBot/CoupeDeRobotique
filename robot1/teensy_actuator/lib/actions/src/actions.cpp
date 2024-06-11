#include <actions.h>

#define FORWARD 1
#define REVERSE 0

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
        else if (msg[0] == NACK)
        {
            // send again the message that wasn't received by the rasp
            com->send_msg((byte *)&com->last_msg->msg, com->last_msg->size, true);
        }
        else
        {
            msg_Unknown_Msg_Type error_message;
            error_message.type_id = msg[0];
            com->send_msg((byte *)&error_message, sizeof(msg_Unknown_Msg_Type)); // raise an error by sending 255 to the rasp if it tries to send a message that isn't defined by the teensy
        }
    }
}

/**
 * Moves the servo to the specified angle.
 *
 * @param servo Pointer to the Servo object.
 * @param angle The angle to which the servo should be moved in degrees.
 */
void servo_go_to(Servo *servo, int angle)
{
    servo->write(angle);
}

void stepper_step(Bonezegei_A4988 *stepper, int steps, bool forward, byte pin_driver)
{
    digitalWrite(pin_driver, LOW);

    if (forward)
        stepper->step(FORWARD, steps);
    else
        stepper->step(REVERSE, steps);

    digitalWrite(pin_driver, HIGH);
}

void lcd_print(LiquidCrystal_I2C *lcd, String text)
{
    lcd->clear();
    if(text.length() > 16)
    {
        String text1 = text.substring(0, 16); // (16 is the number of columns of the lcd screen
        lcd->print(text1);
        lcd->setCursor(0, 1);
        String text2 = text.substring(16, text.length());
        lcd->print(text2);
    } // if the text is too long, it will be cut to fit the lcd screen
    else
    {
        lcd->print(text);
    }
        
    
}
