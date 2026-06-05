// Arena vision system — C++17 rewrite.
// Capture (CSI/GStreamer) -> ArUco detect -> homography -> LoRa game output.

#include <atomic>
#include <chrono>
#include <csignal>
#include <cstdio>
#include <string>
#include <thread>

#include <opencv2/core.hpp>

#include "capture.hpp"
#include "config.hpp"
#include "detector.hpp"
#include "homography.hpp"
#include "lora.hpp"
#include "match_state.hpp"
#include "pipeline.hpp"
#include "protocol.hpp"

namespace {
std::atomic<bool> g_stop{false};
void on_signal(int) { g_stop = true; }
}  // namespace

int main() {
    using namespace av;

    std::signal(SIGINT, on_signal);
    std::signal(SIGTERM, on_signal);

    Config cfg = Config::from_env();
    cfg.print();

    // Let OpenCV's internal parallel_for_ (incl. ArUco) use all cores.
    cv::setNumThreads(cfg.num_threads);

    MatchState match;
    LoRa lora(cfg.lora_port, cfg.lora_baud, cfg.dummy_lora);

    // Incoming LoRa commands.
    lora.register_handler(1, [&](const std::vector<std::string>&) {
        int pid = match.register_pami();
        lora.queue_send(protocol::build_cmd2(pid));
        std::printf("PAMI registered: id=%d\n", pid);
    });
    lora.register_handler(4, [&](const std::vector<std::string>& args) {
        if (args.empty()) {
            std::printf("cmd 4 received without color — ignored\n");
            return;
        }
        if (match.start_match(args[0]))
            std::printf("Match started, team=%s\n", args[0].c_str());
    });

    if (!lora.connect()) {
        std::printf("LoRa unavailable — aborting (set DUMMY_LORA=1 to bypass)\n");
        return 1;
    }
    lora.start();

    Homography homo;
    GameLogic logic(cfg, match, lora);

    int rc = 0;

    if (cfg.dummy_detection) {
        std::printf("DUMMY_DETECTION: synthetic world @ %d fps\n", cfg.sensor_fps);
        const auto period = std::chrono::duration<double>(1.0 / cfg.sensor_fps);
        while (!g_stop) {
            double now = monotonic_seconds();
            logic.process(generate_fake_world(now), now);
            std::this_thread::sleep_for(
                std::chrono::duration_cast<std::chrono::milliseconds>(period));
        }
    } else {
        Capture cap(cfg);
        if (!cap.open()) {
            rc = 1;
        } else {
            std::printf("Source: %s\n", cap.pipeline_desc().c_str());
            Detector det(cfg);
            Pipeline pipe(cap, det, homo, logic, cfg);
            pipe.run(g_stop);
        }
    }

    std::printf("\nShutting down...\n");
    lora.stop();
    lora.disconnect();
    return rc;
}
