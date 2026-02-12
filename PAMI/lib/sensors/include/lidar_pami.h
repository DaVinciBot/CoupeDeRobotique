#ifndef lidar_scanner_h
#define lidar_scanner_h

#include <Arduino.h>

/**
 * @brief Lightweight driver wrapper for the specific LIDAR used on PAMI.
 *
 * This class handles serial reception of LIDAR packets, offers simple
 * convenience methods (for example, `obstacleAhead`) and exposes a callback
 * when a full scan frame is available.
 *
 * Contract / behavior summary:
 *
 * - The serial port is configured in `begin()`; call `update()` frequently to
 *   process incoming bytes and complete frames.
 *
 * - `onReceive()` registers a callback invoked when a full valid frame has
 *   been parsed into the internal buffer.
 */
class lidar_pami {
   public:
    // Default UART baud rate for the LIDAR.
    static constexpr uint32_t DEFAULT_BAUD = 921600;

    /**
     * @brief Construct a new lidar_pami object
     *
     * @param serialPort Reference to the HardwareSerial instance used by the
     * LIDAR
     * @param rxPin UART RX pin, or -1 to use default
     * @param txPin UART TX pin, or -1 to use default
     * @param debug If true, debug prints are emitted on Serial
     *
     * @note the serial port itself is not started until `begin()` is called.
     */
    lidar_pami(HardwareSerial& serialPort,
               int8_t rxPin = -1,
               int8_t txPin = -1,
               bool debug = false);

    /**
     * @brief Initialize the LIDAR serial port and internal state.
     *
     * @param baud Baud rate to use (defaults to `DEFAULT_BAUD`).
     */
    void begin(uint32_t baud = DEFAULT_BAUD);

    /**
     * @brief Convenience helper to determine if an obstacle is in front.
     *
     * @param distanceMin Threshold distance in millimetres (default 100 mm).
     * @return true if an obstacle closer than `distanceMin` was detected
     * @return false otherwise
     */
    bool obstacleAhead(uint16_t distanceMin = 100);

    /**
     * @brief Check a digital input (tirette/push) value from the LIDAR scanner.
     *
     * @param threshold Threshold to consider the tirette engaged
     * @return true if the tirette is on
     * @return false otherwise
     */
    bool isTiretteOn(uint16_t threshold = 25);

    /**
     * @brief Main processing loop: call regularly to process incoming bytes
     * and detect complete frames.
     */
    void update();

    /**
     * @brief Register a callback invoked when a full scan/frame is available.
     *
     * The callback receives no parameters; users should read data via
     * provided accessors or capture required references in their callback.
     */
    void onReceive(void (*callback)());

   private:
    static const uint16_t PACKET_SIZE = 331;   // Expected packet buffer size
    static const uint8_t FRAME_HEADER = 0xA5;  // Frame header marker
    static const uint8_t HEADER_LEN = 8;       // Header length in bytes
    static const uint8_t ENV_LEN = 2;          // Extra envelope length
    static const uint16_t POINT_COUNT = 160;   // Number of points per scan

    HardwareSerial& _serial;  // UART used to communicate with LIDAR
    int8_t _rxPin;            // RX pin (if hardware supports remapping)
    int8_t _txPin;            // TX pin (if hardware supports remapping)
    bool _debug;              // If true, prints debug info

    uint8_t _buffer[PACKET_SIZE];  // Temporary buffer for incoming frame
    uint16_t _bufferIndex = 0;     // Current index in the buffer

    void (*_onReceiveCallback)() = nullptr;  // User callback on full-frame

    /**
     * @brief Try to read and parse a full frame from the serial buffer.
     *
     * @return true if a valid frame was parsed and stored in `_buffer`.
     * @return false otherwise
     */
    bool readFrame();

    /**
     * @brief Send the scan command to the LIDAR to request a fresh scan.
     */
    void sendScanCommand();
};

#endif  // LIDAR_SCANNER_H
