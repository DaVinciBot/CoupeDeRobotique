#include "arena.hpp"

namespace av {
namespace arena {

const StartZone start_blue{1, 0.000, 0.000, 0.6, 0.45};
const StartZone start_yellow{0, 2.400, 0.000, 0.6, 0.45};

const std::vector<Zone> zone_depot = {
    {12, 2.200, 1.800, 0.2, 0.2},
    {20, 1.400, 1.800, 0.2, 0.2},
    {16, 0.600, 1.800, 0.2, 0.2},
    {11, 2.800, 1.100, 0.2, 0.2},
    {14, 2.100, 1.100, 0.2, 0.2},
    {19, 1.400, 1.100, 0.2, 0.2},
    {18, 0.700, 1.100, 0.2, 0.2},
    {15, 0.000, 1.100, 0.2, 0.2},
    {13, 1.650, 0.450, 0.2, 0.2},
    {17, 1.150, 0.450, 0.2, 0.2},
};

const std::vector<Zone> zone_ramassage = {
    {7, 0.100, 0.700, 0.15, 0.2},
    {8, 0.100, 1.500, 0.15, 0.2},
    {3, 2.750, 0.700, 0.15, 0.2},
    {4, 2.750, 1.500, 0.15, 0.2},
    {10, 1.050, 1.125, 0.2, 0.15},
    {6, 1.750, 1.125, 0.2, 0.15},
    {9, 1.000, 1.725, 0.2, 0.15},
    {5, 1.800, 1.725, 0.2, 0.15},
};

int find_zone_for_kapla(double x, double y, double tol) {
    auto in = [&](const Zone& z) {
        return (z.x - tol <= x && x <= z.x + z.w + tol &&
                z.y - tol <= y && y <= z.y + z.h + tol);
    };
    for (const auto& z : zone_depot) if (in(z)) return z.id_zone;
    for (const auto& z : zone_ramassage) if (in(z)) return z.id_zone;
    return -1;
}

}  // namespace arena
}  // namespace av
