#pragma once
// Frame source + preprocessing.
//   - CSI camera via GStreamer NVMM pipeline (GRAY8 output, no CPU cvtColor), or
//   - an image / video file (INPUT_FILE) for off-Jetson testing.
// Preprocess: optional undistortion (calibration) + optional downscale, on GPU
// when OpenCV is built with CUDA, else CPU.

#include <string>

#include <opencv2/core.hpp>

#include "config.hpp"

#ifdef HAVE_CUDA_PREPROC
#include <opencv2/core/cuda.hpp>
#endif

namespace av {

class Capture {
public:
    explicit Capture(const Config& cfg);

    bool open();                       // open camera/file; false on failure
    bool grab(cv::Mat& gray_out);      // fetch + preprocess one frame
    std::string pipeline_desc() const { return desc_; }

private:
    void preprocess(const cv::Mat& in, cv::Mat& gray_out);

    Config cfg_;
    cv::VideoCapture cap_;
    cv::Mat still_;            // for single-image input
    bool is_still_ = false;
    bool use_cuda_ = false;
    bool undistort_ = false;
    cv::Mat map1_, map2_;      // undistortion maps
    std::string desc_;         // human-readable source description

#ifdef HAVE_CUDA_PREPROC
    // Distinct buffers per stage to avoid in-place aliasing.
    cv::cuda::GpuMat g_in_, g_gray_, g_und_, g_ds_, g_map1_, g_map2_;
#endif
};

}  // namespace av
