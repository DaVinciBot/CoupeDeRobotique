#include "homography.hpp"

#include <cmath>
#include <set>

#include <opencv2/calib3d.hpp>

namespace av {

namespace {

cv::Point2f mean_corner(const std::vector<cv::Point2f>& c) {
    cv::Point2f s(0.f, 0.f);
    for (const auto& p : c) s += p;
    return s * (1.0f / static_cast<float>(c.size()));
}

// Normalize to (-pi, pi], matching ((a+pi) % 2pi) - pi in Python.
double norm_angle(double a) {
    double t = std::fmod(a + PI, 2.0 * PI);
    if (t < 0) t += 2.0 * PI;
    return t - PI;
}

}  // namespace

Homography::Homography() {
    // Reference marker world positions, metres -> millimetres.
    ref_world_mm_[20] = {600.0, 1400.0};
    ref_world_mm_[21] = {2400.0, 1400.0};
    ref_world_mm_[22] = {600.0, 600.0};
    ref_world_mm_[23] = {2400.0, 600.0};
}

bool Homography::compute_from_refs(
    const std::vector<int>& ids,
    const std::vector<std::vector<cv::Point2f>>& corners, double now) {
    std::vector<cv::Point2f> src;  // image px
    std::vector<cv::Point2f> dst;  // arena mm
    std::set<int> visible;

    for (size_t i = 0; i < ids.size(); ++i) {
        auto it = ref_world_mm_.find(ids[i]);
        if (it == ref_world_mm_.end()) continue;
        cv::Point2f center = mean_corner(corners[i]);
        src.push_back(center);
        dst.emplace_back(static_cast<float>(it->second.x),
                         static_cast<float>(it->second.y));
        last_seen_[ids[i]] = {center, now};
        visible.insert(ids[i]);
    }

    // Backfill from cache if we have 3 or fewer live refs.
    if (src.size() <= 3) {
        for (const auto& kv : ref_world_mm_) {
            int mid = kv.first;
            if (visible.count(mid)) continue;
            auto c = last_seen_.find(mid);
            if (c == last_seen_.end()) continue;
            if (now - c->second.second > ref_cache_timeout_) continue;
            src.push_back(c->second.first);
            dst.emplace_back(static_cast<float>(kv.second.x),
                             static_cast<float>(kv.second.y));
            if (src.size() >= 4) break;
        }
    }

    const size_t n = src.size();
    if (n < 3) {
        type_ = Type::None;
        return false;
    }

    if (n >= 4) {
        cv::Mat H = cv::findHomography(src, dst, cv::RANSAC, 5.0);
        if (H.empty()) {
            type_ = Type::None;
            return false;
        }
        H_ = H;
        type_ = Type::Homography;
    } else {  // exactly 3 -> affine
        std::vector<cv::Point2f> s3(src.begin(), src.begin() + 3);
        std::vector<cv::Point2f> d3(dst.begin(), dst.begin() + 3);
        A_ = cv::getAffineTransform(s3, d3);
        type_ = Type::Affine;
    }
    return true;
}

std::vector<cv::Point2d> Homography::project(
    const std::vector<cv::Point2f>& pts) const {
    std::vector<cv::Point2d> out;
    out.reserve(pts.size());

    if (type_ == Type::Homography) {
        std::vector<cv::Point2f> dst;
        cv::perspectiveTransform(pts, dst, H_);  // mm
        for (const auto& p : dst)
            out.emplace_back(p.x / 1000.0, p.y / 1000.0);  // -> metres
    } else if (type_ == Type::Affine) {
        const double* a = A_.ptr<double>(0);
        const double* b = A_.ptr<double>(1);
        for (const auto& p : pts) {
            double xmm = a[0] * p.x + a[1] * p.y + a[2];
            double ymm = b[0] * p.x + b[1] * p.y + b[2];
            out.emplace_back(xmm / 1000.0, ymm / 1000.0);
        }
    }
    return out;
}

std::vector<WorldMarker> Homography::localize(
    const std::vector<int>& ids,
    const std::vector<std::vector<cv::Point2f>>& corners) const {
    std::vector<WorldMarker> world;
    if (type_ == Type::None) return world;

    const size_t n = ids.size();
    // Per marker: center, corner0, corner1.
    std::vector<cv::Point2f> pts;
    pts.reserve(n * 3);
    for (size_t i = 0; i < n; ++i) {
        pts.push_back(mean_corner(corners[i]));
        pts.push_back(corners[i][0]);
        pts.push_back(corners[i][1]);
    }

    std::vector<cv::Point2d> w = project(pts);
    if (w.empty()) return world;

    for (size_t i = 0; i < n; ++i) {
        const cv::Point2d& pos = w[i * 3];
        const cv::Point2d& c0 = w[i * 3 + 1];
        const cv::Point2d& c1 = w[i * 3 + 2];
        if (!std::isfinite(pos.x) || !std::isfinite(pos.y) ||
            !std::isfinite(c0.x) || !std::isfinite(c0.y) ||
            !std::isfinite(c1.x) || !std::isfinite(c1.y))
            continue;

        double yaw = std::atan2(c1.y - c0.y, c1.x - c0.x) + PI / 2.0;
        yaw = norm_angle(yaw);

        WorldMarker m;
        m.id = ids[i];
        m.pos_m = pos;
        m.yaw_rad = yaw;
        world.push_back(m);
    }
    return world;
}

}  // namespace av
