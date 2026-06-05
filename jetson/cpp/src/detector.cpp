#include "detector.hpp"

#include <future>
#include <set>
#include <utility>

namespace av {

namespace {

// Apply the Python speed-tuned ArUco parameters to a params object.
template <typename P>
void tune(P& p) {
    p.adaptiveThreshWinSizeMin = 3;
    p.adaptiveThreshWinSizeMax = 23;
    p.adaptiveThreshWinSizeStep = 10;
    p.minMarkerPerimeterRate = 0.02;
    p.polygonalApproxAccuracyRate = 0.06;
    p.minCornerDistanceRate = 0.02;
    p.perspectiveRemovePixelPerCell = 4;
    p.perspectiveRemoveIgnoredMarginPerCell = 0.2;
    p.maxErroneousBitsInBorderRate = 0.6;
    p.cornerRefinementMethod = cv::aruco::CORNER_REFINE_NONE;
}

}  // namespace

Detector::Detector(const Config& cfg) {
    tiled_ = (cfg.detect_parallel == "tile");

#if AV_ARUCO_NEW_API
    cv::aruco::Dictionary dict =
        cv::aruco::getPredefinedDictionary(cv::aruco::DICT_4X4_100);
    cv::aruco::DetectorParameters params;
    tune(params);
    detector_ = cv::aruco::ArucoDetector(dict, params);
#else
    dict_ = cv::aruco::getPredefinedDictionary(cv::aruco::DICT_4X4_100);
    params_ = cv::aruco::DetectorParameters::create();
    tune(*params_);
#endif
}

void Detector::detect_full(
    const cv::Mat& gray, std::vector<int>& ids,
    std::vector<std::vector<cv::Point2f>>& corners) const {
    std::vector<std::vector<cv::Point2f>> rejected;
#if AV_ARUCO_NEW_API
    detector_.detectMarkers(gray, corners, ids, rejected);
#else
    cv::aruco::detectMarkers(gray, dict_, corners, ids, params_, rejected);
#endif
}

void Detector::detect_tiled(
    const cv::Mat& gray, std::vector<int>& ids,
    std::vector<std::vector<cv::Point2f>>& corners) const {
    const int w = gray.cols, h = gray.rows;
    const int overlap = 100;
    const int tw = w / 2 + overlap;
    const int th = h / 2 + overlap;
    const struct { int ox, oy; } tiles[4] = {
        {0, 0}, {w - tw, 0}, {0, h - th}, {w - tw, h - th}};

    // Detect each tile concurrently; corners are reprojected to full-image space.
    auto work = [&](int ox, int oy) {
        cv::Rect roi(ox, oy, tw, th);
        roi &= cv::Rect(0, 0, w, h);
        cv::Mat tile = gray(roi);
        std::vector<int> tids;
        std::vector<std::vector<cv::Point2f>> tcorners, trej;
#if AV_ARUCO_NEW_API
        detector_.detectMarkers(tile, tcorners, tids, trej);
#else
        cv::aruco::detectMarkers(tile, dict_, tcorners, tids, params_, trej);
#endif
        for (auto& mc : tcorners)
            for (auto& pt : mc) {
                pt.x += roi.x;
                pt.y += roi.y;
            }
        return std::make_pair(std::move(tids), std::move(tcorners));
    };

    std::vector<std::future<std::pair<std::vector<int>,
                                      std::vector<std::vector<cv::Point2f>>>>>
        futs;
    for (const auto& t : tiles)
        futs.push_back(std::async(std::launch::async, work, t.ox, t.oy));

    std::set<int> seen;
    for (auto& f : futs) {
        auto res = f.get();
        for (size_t i = 0; i < res.first.size(); ++i) {
            int id = res.first[i];
            if (seen.count(id)) continue;  // dedup overlapping detections
            seen.insert(id);
            ids.push_back(id);
            corners.push_back(std::move(res.second[i]));
        }
    }
}

void Detector::detect(const cv::Mat& gray, std::vector<int>& ids,
                      std::vector<std::vector<cv::Point2f>>& corners) const {
    ids.clear();
    corners.clear();
    if (tiled_)
        detect_tiled(gray, ids, corners);
    else
        detect_full(gray, ids, corners);
}

}  // namespace av
