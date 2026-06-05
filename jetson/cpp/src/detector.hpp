#pragma once
// ArUco DICT_4X4_100 detector wrapper. Tuned for speed (matches the Python
// DetectorParameters). Optional 2x2 tiled detection for extra parallelism.

#include <vector>

#include <opencv2/core.hpp>
#include <opencv2/aruco.hpp>

#include "config.hpp"

// OpenCV >= 4.7 uses the ArucoDetector class + value-typed Dictionary/params.
#if CV_VERSION_MAJOR > 4 || (CV_VERSION_MAJOR == 4 && CV_VERSION_MINOR >= 7)
#define AV_ARUCO_NEW_API 1
#else
#define AV_ARUCO_NEW_API 0
#endif

namespace av {

class Detector {
public:
    explicit Detector(const Config& cfg);

    // Detect markers in a single-channel image. Outputs in image pixel space.
    void detect(const cv::Mat& gray, std::vector<int>& ids,
                std::vector<std::vector<cv::Point2f>>& corners) const;

private:
    void detect_full(const cv::Mat& gray, std::vector<int>& ids,
                     std::vector<std::vector<cv::Point2f>>& corners) const;
    void detect_tiled(const cv::Mat& gray, std::vector<int>& ids,
                      std::vector<std::vector<cv::Point2f>>& corners) const;

    bool tiled_ = false;

#if AV_ARUCO_NEW_API
    cv::aruco::ArucoDetector detector_;
#else
    cv::Ptr<cv::aruco::Dictionary> dict_;
    cv::Ptr<cv::aruco::DetectorParameters> params_;
#endif
};

}  // namespace av
