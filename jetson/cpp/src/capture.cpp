#include "capture.hpp"

#include <cstdio>

#include <opencv2/calib3d.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/videoio.hpp>

#ifdef HAVE_CUDA_PREPROC
#include <opencv2/cudaimgproc.hpp>
#include <opencv2/cudawarping.hpp>
#endif

namespace av {

namespace {

std::string build_gst_pipeline(const Config& c) {
    char buf[512];
    std::snprintf(
        buf, sizeof(buf),
        "nvarguscamerasrc sensor-id=%d sensor-mode=0 ! "
        "video/x-raw(memory:NVMM),width=%d,height=%d,format=NV12,framerate=%d/1 ! "
        "nvvidconv flip-method=0 ! "
        "video/x-raw,width=%d,height=%d,format=GRAY8 ! "
        "appsink max-buffers=1 drop=true sync=false",
        c.camera_id, c.sensor_width, c.sensor_height, c.sensor_fps,
        c.sensor_width, c.sensor_height);
    return buf;
}

}  // namespace

Capture::Capture(const Config& cfg) : cfg_(cfg) {}

bool Capture::open() {
#ifdef HAVE_CUDA_PREPROC
    use_cuda_ = cv::cuda::getCudaEnabledDeviceCount() > 0;
#endif

    if (!cfg_.input_file.empty()) {
        // Try as a still image first, then as a video file.
        cv::Mat img = cv::imread(cfg_.input_file, cv::IMREAD_UNCHANGED);
        if (!img.empty()) {
            still_ = img;
            is_still_ = true;
            desc_ = "image: " + cfg_.input_file;
        } else if (cap_.open(cfg_.input_file)) {
            desc_ = "video: " + cfg_.input_file;
        } else {
            std::printf("Capture: cannot open input '%s'\n",
                        cfg_.input_file.c_str());
            return false;
        }
    } else {
        desc_ = build_gst_pipeline(cfg_);
        if (!cap_.open(desc_, cv::CAP_GSTREAMER)) {
            std::printf("Capture: failed to open CSI camera (GStreamer)\n");
            return false;
        }
    }

    // Optional undistortion maps from a calibration file.
    if (!cfg_.calibration_file.empty()) {
        cv::FileStorage fs(cfg_.calibration_file, cv::FileStorage::READ);
        if (fs.isOpened()) {
            cv::Mat K, dist;
            fs["camera_matrix"] >> K;
            fs["dist_coeffs"] >> dist;
            if (!K.empty() && !dist.empty()) {
                cv::Size size(cfg_.sensor_width, cfg_.sensor_height);
                cv::Mat newK =
                    cv::getOptimalNewCameraMatrix(K, dist, size, 0.0);
                // CV_32FC1 maps work for both cv::remap and cv::cuda::remap.
                cv::initUndistortRectifyMap(K, dist, cv::Mat(), newK, size,
                                            CV_32FC1, map1_, map2_);
                undistort_ = true;
#ifdef HAVE_CUDA_PREPROC
                if (use_cuda_) {
                    g_map1_.upload(map1_);
                    g_map2_.upload(map2_);
                }
#endif
                std::printf("Capture: undistortion enabled from %s\n",
                            cfg_.calibration_file.c_str());
            }
        } else {
            std::printf("Capture: calibration file '%s' not readable\n",
                        cfg_.calibration_file.c_str());
        }
    }
    return true;
}

void Capture::preprocess(const cv::Mat& in, cv::Mat& gray_out) {
    const double ds = cfg_.detect_downscale > 1.0 ? cfg_.detect_downscale : 1.0;

#ifdef HAVE_CUDA_PREPROC
    if (use_cuda_) {
        g_in_.upload(in);
        cv::cuda::GpuMat* cur = &g_in_;
        if (in.channels() == 3) {
            cv::cuda::cvtColor(*cur, g_gray_, cv::COLOR_BGR2GRAY);
            cur = &g_gray_;
        }
        if (undistort_) {
            cv::cuda::remap(*cur, g_und_, g_map1_, g_map2_, cv::INTER_LINEAR);
            cur = &g_und_;
        }
        if (ds > 1.0) {
            cv::Size ns(static_cast<int>(in.cols / ds),
                        static_cast<int>(in.rows / ds));
            cv::cuda::resize(*cur, g_ds_, ns);  // distinct dst, no aliasing
            cur = &g_ds_;
        }
        cur->download(gray_out);
        return;
    }
#endif

    cv::Mat g;
    if (in.channels() == 3)
        cv::cvtColor(in, g, cv::COLOR_BGR2GRAY);
    else
        g = in;
    if (undistort_) {
        cv::Mat u;
        cv::remap(g, u, map1_, map2_, cv::INTER_LINEAR);
        g = u;
    }
    if (ds > 1.0) {
        cv::Size ns(static_cast<int>(g.cols / ds),
                    static_cast<int>(g.rows / ds));
        cv::resize(g, gray_out, ns, 0, 0, cv::INTER_AREA);
    } else {
        gray_out = g;
    }
}

bool Capture::grab(cv::Mat& gray_out) {
    cv::Mat frame;
    if (is_still_) {
        frame = still_;
    } else {
        if (!cap_.read(frame) || frame.empty()) return false;
    }
    preprocess(frame, gray_out);
    return !gray_out.empty();
}

}  // namespace av
