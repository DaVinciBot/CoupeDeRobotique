#include <Arduino.h>
#include <messages.h>

/**
 * @brief Structure to store the last sent message.
 *
 * This structure keeps track of the size and content of the last message
 * sent by the communication system. It is used to handle retransmissions
 * in case of a NACK (Negative Acknowledgment).
 */
struct last_message {
    byte size;      ///< Size of the message in bytes
    byte msg[256];  ///< Content of the message
};

/**
 * @brief Communication (Com) class for serial communication.
 *
 * This class facilitates communication over a serial interface. It provides
 * methods for handling incoming messages, managing callbacks, and sending
 * messages. The class also implements message buffering, signature validation,
 * and retransmission handling.
 */
class Com {
   private:
    byte* buffer =
        new byte[256];  ///< Internal buffer for storing received data
    byte signature[4];  ///< Signature used to validate messages (default:
                        ///< END_BYTES_SIGNATURE) initialized in the constructor
    byte pointer = 0;   ///< Pointer for tracking the buffer position
    Stream* stream;     ///< Pointer to the serial stream (USB or Hardware)

   public:
    /**
     * @brief Constructor for USB serial communication.
     *
     * Initializes the communication stream for USB serial and sets the baud
     * rate.
     *
     * @param stream Pointer to the USB serial class.
     * @param baudrate Baud rate for serial communication.
     */
    Com(usb_serial_class* stream, uint32_t baudrate);

    /**
     * @brief Constructor for hardware serial communication.
     *
     * Initializes the communication stream for hardware serial and sets the
     * baud rate.
     *
     * @param stream Pointer to the hardware serial class.
     * @param baudrate Baud rate for serial communication.
     */
    Com(HardwareSerial* stream, uint32_t baudrate);

    /**
     * @brief Handles incoming data from the communication stream.
     *
     * Processes data received from the serial stream, validates it using the
     * signature, and extracts the message size if a valid message is detected.
     *
     * @return The size of the valid message, or 0 if no valid message is found.
     */
    byte handle();

    /**
     * @brief Handles callbacks for received messages.
     *
     * Retrieves the message ID from the received message and calls the
     * corresponding callback function from the provided array of function
     * pointers.
     *
     * @param functions Array of callback functions indexed by message ID.
     */
    void handle_callback(void (*functions[256])(byte* msg, byte size));

    /**
     * @brief Provides access to the internal buffer.
     *
     * @return Pointer to the internal buffer containing the received data.
     */
    byte* read_buffer();

    /**
     * @brief Sends a message over the communication stream.
     *
     * Prepares the message with size and optional NACK flag, computes the
     * checksum, and transmits the message along with the signature.
     *
     * @param msg Pointer to the message data to send.
     * @param size Size of the message data.
     * @param is_nack Indicates if the message is a retransmission due to a NACK
     * (default: false).
     */
    void send_msg(byte* msg, byte size, bool is_nack = false);

    /**
     * @brief Sends a debug text message.
     *
     * This function sends a text message for debugging purposes. The message
     * must be in ASCII format and cannot exceed 253 characters.
     *
     * @param text Pointer to the null-terminated ASCII text string to send.
     */
    void print(char* text);

    last_message* last_msg =
        new last_message();  ///< Pointer to the last sent message for
                             ///< retransmission
};
