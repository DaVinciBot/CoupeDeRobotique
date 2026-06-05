#pragma once
// Runtime configuration, populated from environment variables.
// Mirrors the .env-based config of the original Python system.

#include <string>

namespace av {

struct Config {
    // Camera / capture
    int camera_id = 0;
    int sensor_width = 3280;
    int sensor_height = 2464;
    int sensor_fps = 21;
    double detect_downscale = 1.0;   // >1.0 downscales before detection

    // Detection
    int num_threads = 6;             // OpenCV parallel_for_ thread count (Orin Nano = 6)
    std::string detect_parallel = "off";  // off | tile | frame

    // Marker IDs (semantics from the arena rules)
    int robot_marker_id = 6;         // ally
    int enemy_marker_id = 1;
    int blue_crate_id = 36;
    int yellow_crate_id = 47;
    int empty_crate_id = 41;

    // Zone classification tolerance
    double zone_tolerance_m = 0.05;  // ZONE_TOLERANCE_CM / 100

    // LoRa
    std::string lora_port = "/dev/ttyTHS1";
    int lora_baud = 115200;

    // Optional camera calibration (OpenCV FileStorage .yml/.xml)
    std::string calibration_file;

    // Modes
    bool dummy_lora = false;
    bool dummy_detection = false;
    std::string input_file;          // image/video instead of CSI camera
    bool debug_mode = false;
    bool enable_keyboard = false;

    static Config from_env();
    void print() const;
};

}  // namespace av
