#include "tracking.hpp"

#include <cmath>

namespace av {

void SpeedTracker::update(int id, double t, double x, double y) {
    auto& dq = hist_[id];
    dq.push_back({t, x, y});
    while (dq.size() > max_) dq.pop_front();
}

double SpeedTracker::speed(int id) const {
    auto it = hist_.find(id);
    if (it == hist_.end()) return 0.0;
    const auto& dq = it->second;
    if (dq.size() < 2) return 0.0;
    const auto& a = dq.front();
    const auto& b = dq.back();
    double dt = b[0] - a[0];
    if (dt < 0.01) return 0.0;
    double dx = b[1] - a[1];
    double dy = b[2] - a[2];
    return std::sqrt(dx * dx + dy * dy) / dt;
}

}  // namespace av
