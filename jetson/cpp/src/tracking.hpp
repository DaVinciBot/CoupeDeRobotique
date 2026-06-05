#pragma once
// Robot speed tracking from a short position history.
// Equivalent to compute_speed() + robot_position_history in python/main.py.

#include <array>
#include <cstddef>
#include <deque>
#include <unordered_map>

namespace av {

class SpeedTracker {
public:
    explicit SpeedTracker(std::size_t max_samples = 15) : max_(max_samples) {}

    // Append a position sample (time seconds, x, y metres) for a tracked id.
    void update(int id, double t, double x, double y);

    // Linear speed in m/s over the stored window; 0 if insufficient data.
    double speed(int id) const;

private:
    std::size_t max_;
    std::unordered_map<int, std::deque<std::array<double, 3>>> hist_;  // {t,x,y}
};

}  // namespace av
