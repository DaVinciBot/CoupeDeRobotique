#pragma once
// Image -> arena coordinate transform from reference markers.
// Mirrors compute_transform_from_refs / transform_points_to_world_batch in
// python/src/detector/detector.py. Internally works in millimetres.

#include <map>
#include <utility>
#include <vector>

#include <opencv2/core.hpp>

#include "types.hpp"

namespace av {

class Homography {
public:
    Homography();

    // Recompute the transform from currently visible reference markers
    // (ids 20/21/22/23), backfilling missing refs from a cached position
    // (<=20s old). >=4 refs -> homography (RANSAC); ==3 -> affine; <3 -> none.
    // Returns true if a transform is available.
    bool compute_from_refs(const std::vector<int>& ids,
                           const std::vector<std::vector<cv::Point2f>>& corners,
                           double now);

    bool valid() const { return type_ != Type::None; }

    // Localize every detected marker: center -> arena metres, yaw from
    // corner0->corner1. Markers that project to infinity are dropped.
    std::vector<WorldMarker> localize(
        const std::vector<int>& ids,
        const std::vector<std::vector<cv::Point2f>>& corners) const;

private:
    enum class Type { None, Homography, Affine };

    // Project image points (px) to arena points (metres).
    std::vector<cv::Point2d> project(const std::vector<cv::Point2f>& pts) const;

    std::map<int, cv::Point2d> ref_world_mm_;                  // id -> (x_mm, y_mm)
    std::map<int, std::pair<cv::Point2f, double>> last_seen_;  // id -> (center, time)
    double ref_cache_timeout_ = 20.0;

    cv::Mat H_;  // 3x3 CV_64F, image px -> arena mm
    cv::Mat A_;  // 2x3 CV_64F, image px -> arena mm
    Type type_ = Type::None;
};

}  // namespace av
