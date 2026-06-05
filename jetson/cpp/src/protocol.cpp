#include "protocol.hpp"

#include <array>
#include <cmath>
#include <cstdio>
#include <string>

#include "arena.hpp"

namespace av {
namespace protocol {

namespace {

// _enc_xy: meters -> round(m * 100 * 10) == round(m * 1000). Also used for speed (m/s).
long enc_xy(double meters) { return std::lround(meters * 1000.0); }

// _enc_angle: radians -> round(rad * 1000).
long enc_angle(double radians) { return std::lround(radians * 1000.0); }

}  // namespace

std::string build_cmd5(const std::vector<WorldMarker>& world,
                       const std::unordered_map<int, double>& robot_speeds,
                       const Config& cfg) {
    long robot[3] = {0, 0, 0};
    long enemy[3] = {0, 0, 0};

    for (const auto& m : world) {
        if (m.id == cfg.robot_marker_id) {
            robot[0] = enc_xy(m.pos_m.x);
            robot[1] = enc_xy(m.pos_m.y);
            robot[2] = enc_angle(m.yaw_rad);
        } else if (m.id == cfg.enemy_marker_id) {
            enemy[0] = enc_xy(m.pos_m.x);
            enemy[1] = enc_xy(m.pos_m.y);
            enemy[2] = enc_angle(m.yaw_rad);
        }
    }

    double enemy_speed = 0.0;
    auto it = robot_speeds.find(cfg.enemy_marker_id);
    if (it != robot_speeds.end()) enemy_speed = it->second;

    // Header: 9 fields. (evx, evy unused -> 0,0; espeed encoded like xy.)
    long header[HEADER_FIELDS] = {
        robot[0], robot[1], robot[2],
        enemy[0], enemy[1], enemy[2],
        0, 0, enc_xy(enemy_speed),
    };

    // Crates: up to 32 records of [zone_id, x_enc, y_enc, color_id].
    std::vector<std::array<long, 4>> crates;
    crates.reserve(NUM_CRATES);
    for (const auto& m : world) {
        int color_id;
        if (m.id == cfg.blue_crate_id) color_id = 0;
        else if (m.id == cfg.yellow_crate_id) color_id = 1;
        else if (m.id == cfg.empty_crate_id) color_id = 2;
        else continue;

        int zone_id = arena::find_zone_for_kapla(m.pos_m.x, m.pos_m.y,
                                                 cfg.zone_tolerance_m);
        crates.push_back({static_cast<long>(zone_id),
                          enc_xy(m.pos_m.x), enc_xy(m.pos_m.y),
                          static_cast<long>(color_id)});
        if (static_cast<int>(crates.size()) >= NUM_CRATES) break;
    }
    while (static_cast<int>(crates.size()) < NUM_CRATES) {
        crates.push_back({0, 0, 0, 0});
    }

    std::string out;
    out.reserve(PACKET_FIELDS * 5);
    char buf[32];
    for (int i = 0; i < HEADER_FIELDS; ++i) {
        if (i) out += '|';
        std::snprintf(buf, sizeof(buf), "%ld", header[i]);
        out += buf;
    }
    for (const auto& c : crates) {
        for (int k = 0; k < 4; ++k) {
            out += '|';
            std::snprintf(buf, sizeof(buf), "%ld", c[k]);
            out += buf;
        }
    }
    out += '\n';
    return out;
}

std::string build_cmd2(int pami_id) {
    return "2|" + std::to_string(pami_id) + "\n";
}

}  // namespace protocol
}  // namespace av
