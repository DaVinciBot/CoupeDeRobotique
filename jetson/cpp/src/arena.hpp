#pragma once
// Arena geometry and zone classification.
// Constants transcribed verbatim from python/src/arena/arena_element.py.
// All units are metres; zone positions are the lower-left corner.

#include <vector>

namespace av {
namespace arena {

struct Zone {
    int id_zone;
    double x, y;   // lower-left corner
    double w, h;
};

struct StartZone {
    int id_zone;
    double x, y, w, h;
};

extern const StartZone start_blue;    // id_zone 1, corner (0.000, 0.000)
extern const StartZone start_yellow;  // id_zone 0, corner (2.400, 0.000)
extern const std::vector<Zone> zone_depot;       // 10 depot zones
extern const std::vector<Zone> zone_ramassage;   // 8 pickup zones

// Returns the id_zone containing (x, y) within tolerance, or -1 if none.
// Searches depot zones then pickup zones (same order as the Python _ALL_ZONES).
int find_zone_for_kapla(double x, double y, double tol);

}  // namespace arena
}  // namespace av
