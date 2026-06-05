#pragma once
// LoRa message builders. Wire format: ASCII ints/floats joined by '|', '\n'-terminated.
// cmd-5 reproduces python/main.py:build_lora_message exactly (137-integer packet).

#include <string>
#include <unordered_map>
#include <vector>

#include "config.hpp"
#include "types.hpp"

namespace av {
namespace protocol {

constexpr int NUM_CRATES = 32;
constexpr int HEADER_FIELDS = 9;
constexpr int PACKET_FIELDS = HEADER_FIELDS + NUM_CRATES * 4;  // 137

// cmd 5: vision data.
// Header: rx ry rtheta ex ey etheta 0 0 enemy_speed   (ally=robot_marker_id, enemy=enemy_marker_id)
// Then 32 crates x [zone_id, x_enc, y_enc, color_id], padded with (0,0,0,0).
// Encoding: xy -> round(m*1000); angle -> round(rad*1000); color 36->0,47->1,41->2.
std::string build_cmd5(const std::vector<WorldMarker>& world,
                       const std::unordered_map<int, double>& robot_speeds,
                       const Config& cfg);

// cmd 2: PAMI id assignment.
std::string build_cmd2(int pami_id);

}  // namespace protocol
}  // namespace av
