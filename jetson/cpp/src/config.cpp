#include "config.hpp"

#include <cctype>
#include <cstdlib>
#include <cstdio>
#include <string>

namespace av {

namespace {

const char* get(const char* name) { return std::getenv(name); }

std::string get_str(const char* name, const std::string& def) {
    const char* v = get(name);
    return v ? std::string(v) : def;
}

int get_int(const char* name, int def) {
    const char* v = get(name);
    if (!v || !*v) return def;
    try { return std::stoi(v); } catch (...) { return def; }
}

double get_double(const char* name, double def) {
    const char* v = get(name);
    if (!v || !*v) return def;
    try { return std::stod(v); } catch (...) { return def; }
}

bool get_bool(const char* name, bool def) {
    const char* v = get(name);
    if (!v) return def;
    std::string s(v);
    for (auto& c : s) c = static_cast<char>(std::tolower(c));
    return s == "true" || s == "1" || s == "yes" || s == "on";
}

}  // namespace

Config Config::from_env() {
    Config c;
    c.camera_id = get_int("CAMERA_ID", c.camera_id);
    c.sensor_width = get_int("SENSOR_WIDTH", c.sensor_width);
    c.sensor_height = get_int("SENSOR_HEIGHT", c.sensor_height);
    c.sensor_fps = get_int("SENSOR_FPS", c.sensor_fps);
    c.detect_downscale = get_double("DETECT_DOWNSCALE", c.detect_downscale);

    c.num_threads = get_int("NUM_THREADS", c.num_threads);
    c.detect_parallel = get_str("DETECT_PARALLEL", c.detect_parallel);

    c.robot_marker_id = get_int("ROBOT_MARKER_ID", c.robot_marker_id);
    c.enemy_marker_id = get_int("ENEMY_MARKER_ID", c.enemy_marker_id);
    c.blue_crate_id = get_int("BLUE_CRATE_MARKER_ID", c.blue_crate_id);
    c.yellow_crate_id = get_int("YELLOW_CRATE_MARKER_ID", c.yellow_crate_id);
    c.empty_crate_id = get_int("EMPTY_CRATE_MARKER_ID", c.empty_crate_id);

    c.zone_tolerance_m = get_double("ZONE_TOLERANCE_CM", 5.0) / 100.0;

    c.lora_port = get_str("LORA_PORT", c.lora_port);
    c.lora_baud = get_int("LORA_BAUD", c.lora_baud);

    c.calibration_file = get_str("CALIBRATION_FILE", c.calibration_file);

    c.dummy_lora = get_bool("DUMMY_LORA", c.dummy_lora);
    c.dummy_detection = get_bool("DUMMY_DETECTION", c.dummy_detection);
    c.input_file = get_str("INPUT_FILE", c.input_file);
    c.debug_mode = get_bool("DEBUG_MODE", c.debug_mode);
    c.enable_keyboard = get_bool("ENABLE_KEYBOARD", c.enable_keyboard);
    return c;
}

void Config::print() const {
    std::printf("=== Config ===\n");
    std::printf("  camera_id=%d  sensor=%dx%d@%d  detect_downscale=%.2f\n",
                camera_id, sensor_width, sensor_height, sensor_fps, detect_downscale);
    std::printf("  num_threads=%d  detect_parallel=%s\n",
                num_threads, detect_parallel.c_str());
    std::printf("  ids: robot=%d enemy=%d blue=%d yellow=%d empty=%d\n",
                robot_marker_id, enemy_marker_id, blue_crate_id,
                yellow_crate_id, empty_crate_id);
    std::printf("  zone_tol=%.3fm  lora=%s@%d\n",
                zone_tolerance_m, lora_port.c_str(), lora_baud);
    std::printf("  dummy_lora=%d dummy_detection=%d input_file='%s' debug=%d\n",
                dummy_lora, dummy_detection, input_file.c_str(), debug_mode);
}

}  // namespace av
