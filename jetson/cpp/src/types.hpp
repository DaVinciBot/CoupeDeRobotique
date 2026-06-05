#pragma once
// Shared value types used across the pipeline stages.

#include <chrono>
#include <vector>
#include <opencv2/core.hpp>

namespace av {

constexpr double PI = 3.14159265358979323846;

// Monotonic seconds since process start (single clock base for all timing).
inline double monotonic_seconds() {
    using namespace std::chrono;
    static const auto t0 = steady_clock::now();
    return duration<double>(steady_clock::now() - t0).count();
}

// Raw detector output for one frame, in detection-image pixel space.
struct DetectionFrame {
    std::vector<int> ids;
    std::vector<std::vector<cv::Point2f>> corners;  // 4 corners per marker
    double timestamp = 0.0;                          // monotonic seconds
};

// A marker localized in arena coordinates.
struct WorldMarker {
    int id = 0;
    cv::Point2d pos_m;     // arena position, metres
    double yaw_rad = 0.0;  // heading, radians, normalized to (-pi, pi]
};

}  // namespace av
