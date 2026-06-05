#include "pipeline.hpp"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <utility>
#include <vector>

#include "capture.hpp"
#include "detector.hpp"
#include "homography.hpp"
#include "lora.hpp"
#include "match_state.hpp"
#include "protocol.hpp"

namespace av {

// ---------------- Fake world (DUMMY_DETECTION) ----------------

std::vector<WorldMarker> generate_fake_world(double t) {
    auto mk = [](int id, double x, double y, double yaw) {
        WorldMarker m;
        m.id = id;
        m.pos_m = {x, y};
        m.yaw_rad = yaw;
        return m;
    };
    const double cycle = std::fmod(t, 4.0);
    double progress, r1a, r6a, r1x, r6x;
    if (cycle < 2.0) {
        progress = cycle / 2.0;
        r1a = 0.0;
        r6a = PI;
        r1x = 0.800 + progress * 1.0;
        r6x = 2.200 - progress * 1.0;
    } else {
        progress = (cycle - 2.0) / 2.0;
        r1a = PI;
        r6a = 0.0;
        r1x = 1.800 - progress * 1.0;
        r6x = 1.200 + progress * 1.0;
    }

    std::vector<WorldMarker> w;
    // 4 reference markers
    w.push_back(mk(20, 0.600, 1.400, PI / 2));
    w.push_back(mk(21, 2.400, 1.400, PI / 2));
    w.push_back(mk(22, 0.600, 0.600, PI / 2));
    w.push_back(mk(23, 2.400, 0.600, PI / 2));
    // robots
    w.push_back(mk(1, r1x, 1.000, r1a));
    w.push_back(mk(6, r6x, 1.000, r6a));
    // a representative set of crates (blue=36, yellow=47, empty=41)
    const double q = PI / 2;
    w.push_back(mk(36, 0.175, 0.725, 0.0));
    w.push_back(mk(47, 0.175, 0.775, 0.0));
    w.push_back(mk(36, 2.825, 1.525, 0.0));
    w.push_back(mk(47, 2.825, 1.575, 0.0));
    w.push_back(mk(36, 1.175, 1.800, q));
    w.push_back(mk(47, 1.075, 1.800, q));
    w.push_back(mk(41, 2.250, 0.325, q));
    w.push_back(mk(41, 0.750, 0.325, q));
    // 6 blue PAMIs (51-56), 6 yellow PAMIs (71-76)
    for (int i = 0; i < 6; ++i)
        w.push_back(mk(51 + i, 0.100 + (i % 3) * 0.11, 0.050 + (i % 2) * 0.11, q));
    for (int i = 0; i < 6; ++i)
        w.push_back(mk(71 + i, 2.900 - (i % 3) * 0.11, 0.050 + (i % 2) * 0.11, q));
    return w;
}

// ---------------- GameLogic ----------------

GameLogic::GameLogic(const Config& cfg, MatchState& ms, LoRa& lora)
    : cfg_(cfg), ms_(ms), lora_(lora), speed_(15) {}

void GameLogic::process(const std::vector<WorldMarker>& world, double now) {
    // Robot speeds: only for tracked ids seen this frame (matches Python).
    std::unordered_map<int, double> speeds;
    for (const auto& m : world) {
        if (m.id == cfg_.robot_marker_id || m.id == cfg_.enemy_marker_id) {
            speed_.update(m.id, now, m.pos_m.x, m.pos_m.y);
            speeds[m.id] = speed_.speed(m.id);
        }
    }

    // cmd 3: depot assignments, once at T+90s.
    if (ms_.should_send_pre_end()) {
        auto assignments = ms_.compute_depot_assignments();
        lora_.queue_send(MatchState::build_msg_3(assignments));
        ms_.mark_pre_end_sent();
        std::printf("cmd3 sent: %zu PAMI(s) assigned\n", assignments.size());
    }

    // cmd 5: continuous vision data during the match.
    if (ms_.match_started() && !ms_.is_over()) {
        lora_.queue_send(protocol::build_cmd5(world, speeds, cfg_));
    }

    if (cfg_.debug_mode) {
        std::printf("{\"n\":%zu,\"markers\":[", world.size());
        for (size_t i = 0; i < world.size(); ++i) {
            const auto& m = world[i];
            std::printf("%s{\"id\":%d,\"x\":%.3f,\"y\":%.3f,\"deg\":%.1f}",
                        i ? "," : "", m.id, m.pos_m.x, m.pos_m.y,
                        m.yaw_rad * 180.0 / PI);
        }
        std::printf("]}\n");
    }
}

// ---------------- Pipeline ----------------

Pipeline::Pipeline(Capture& cap, Detector& det, Homography& homo,
                   GameLogic& logic, const Config& cfg)
    : cap_(cap), det_(det), homo_(homo), logic_(logic), cfg_(cfg) {}

void Pipeline::capture_loop() {
    while (running_) {
        TimedFrame f;
        if (!cap_.grab(f.gray)) {
            finished_ = true;
            frame_slot_.close();
            return;
        }
        f.ts = monotonic_seconds();
        frame_slot_.push(std::move(f));
    }
    frame_slot_.close();
}

void Pipeline::detect_loop() {
    while (running_) {
        TimedFrame f;
        if (!frame_slot_.pop(f)) break;
        DetectionFrame d;
        d.timestamp = f.ts;
        det_.detect(f.gray, d.ids, d.corners);
        det_slot_.push(std::move(d));
    }
    det_slot_.close();
}

void Pipeline::logic_loop() {
    while (running_) {
        DetectionFrame d;
        if (!det_slot_.pop(d)) break;
        if (!d.ids.empty()) {
            homo_.compute_from_refs(d.ids, d.corners, d.timestamp);
            auto world = homo_.localize(d.ids, d.corners);
            logic_.process(world, d.timestamp);
        } else {
            logic_.process({}, d.timestamp);
        }
        processed_.fetch_add(1, std::memory_order_relaxed);
    }
}

void Pipeline::run(std::atomic<bool>& stop) {
    running_ = true;

    std::thread cap_t(&Pipeline::capture_loop, this);

    // Detection: N threads for frame-parallel mode, else one.
    int n_det = (cfg_.detect_parallel == "frame")
                    ? std::max(1, cfg_.num_threads)
                    : 1;
    std::vector<std::thread> det_threads;
    for (int i = 0; i < n_det; ++i)
        det_threads.emplace_back(&Pipeline::detect_loop, this);

    std::thread logic_t(&Pipeline::logic_loop, this);

    // Main thread: FPS reporting until stop or input end.
    long last = 0;
    double last_t = monotonic_seconds();
    while (!stop && !finished_) {
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
        double now = monotonic_seconds();
        if (now - last_t >= 1.0) {
            long cur = processed_.load(std::memory_order_relaxed);
            double fps = (cur - last) / (now - last_t);
            if (cfg_.debug_mode)
                std::printf("[fps] %.1f end-to-end\n", fps);
            last = cur;
            last_t = now;
        }
    }

    // Shut down: stop stages and drain.
    running_ = false;
    frame_slot_.close();
    det_slot_.close();
    cap_t.join();
    for (auto& t : det_threads) t.join();
    logic_t.join();
}

}  // namespace av
