#pragma once
// Threaded pipeline orchestration + the game-logic stage.
//
// Stages (each its own thread, handoff via latest-frame-only slots):
//   capture -> [TimedFrame] -> detect -> [DetectionFrame] -> logic/output
//
// GameLogic turns localized markers into LoRa traffic (cmd 3/5) and applies
// speed tracking + match timing.

#include <atomic>
#include <condition_variable>
#include <mutex>
#include <thread>
#include <unordered_map>
#include <vector>

#include <opencv2/core.hpp>

#include "config.hpp"
#include "tracking.hpp"
#include "types.hpp"

namespace av {

class Capture;
class Detector;
class Homography;
class LoRa;
class MatchState;

// Single-slot, latest-wins handoff. push() overwrites; pop() blocks until an
// item is available or the slot is closed.
template <class T>
class LatestSlot {
public:
    void push(T v) {
        {
            std::lock_guard<std::mutex> lk(m_);
            item_ = std::move(v);
            has_ = true;
        }
        cv_.notify_one();
    }
    bool pop(T& out) {
        std::unique_lock<std::mutex> lk(m_);
        cv_.wait(lk, [&] { return has_ || closed_; });
        if (!has_) return false;
        out = std::move(item_);
        has_ = false;
        return true;
    }
    void close() {
        {
            std::lock_guard<std::mutex> lk(m_);
            closed_ = true;
        }
        cv_.notify_all();
    }

private:
    std::mutex m_;
    std::condition_variable cv_;
    T item_;
    bool has_ = false;
    bool closed_ = false;
};

struct TimedFrame {
    cv::Mat gray;
    double ts = 0.0;
};

// Synthetic world for DUMMY_DETECTION (matches generate_fake_detected_world).
std::vector<WorldMarker> generate_fake_world(double t);

class GameLogic {
public:
    GameLogic(const Config& cfg, MatchState& ms, LoRa& lora);
    // Process one frame of localized markers (now = monotonic seconds).
    void process(const std::vector<WorldMarker>& world, double now);

private:
    Config cfg_;
    MatchState& ms_;
    LoRa& lora_;
    SpeedTracker speed_;
};

class Pipeline {
public:
    Pipeline(Capture& cap, Detector& det, Homography& homo, GameLogic& logic,
             const Config& cfg);

    // Run until *stop becomes true or the input ends. Blocks the caller.
    void run(std::atomic<bool>& stop);

private:
    void capture_loop();
    void detect_loop();
    void logic_loop();

    Capture& cap_;
    Detector& det_;
    Homography& homo_;
    GameLogic& logic_;
    Config cfg_;

    LatestSlot<TimedFrame> frame_slot_;
    LatestSlot<DetectionFrame> det_slot_;

    std::atomic<bool> running_{false};
    std::atomic<bool> finished_{false};   // input ended
    std::atomic<long> processed_{0};
};

}  // namespace av
