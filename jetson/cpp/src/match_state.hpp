#pragma once
// Match lifecycle FSM, PAMI id allocation, and depot assignment.
// Mirrors python/src/game/match.py (thread-safe).

#include <chrono>
#include <mutex>
#include <string>
#include <tuple>
#include <vector>

namespace av {

class MatchState {
public:
    static constexpr double MATCH_DURATION = 100.0;  // seconds
    static constexpr double PRE_END_OFFSET = 10.0;   // send cmd 3 at T+90s

    // ---- PAMIs ----
    int register_pami();                 // allocate + return a new id (from 1)
    std::vector<int> pami_ids() const;

    // ---- Lifecycle ----
    bool start_match(const std::string& color);  // "B"/"Y", idempotent
    bool match_started() const;
    std::string team_color() const;     // "" if unset
    double elapsed() const;             // seconds since start, 0 if not started
    bool is_over() const;
    bool should_send_pre_end() const;   // true once when T+90s reached
    void mark_pre_end_sent();

    // ---- Depots ----
    // Greedy: each PAMI -> nearest free depot to our start zone, registration order.
    std::vector<std::tuple<int, double, double>> compute_depot_assignments() const;
    static std::string build_msg_3(
        const std::vector<std::tuple<int, double, double>>& assignments);

private:
    mutable std::mutex m_;
    std::vector<int> pami_ids_;
    int next_pami_id_ = 1;

    std::string team_color_;
    bool match_started_ = false;
    std::chrono::steady_clock::time_point start_ts_;
    bool pre_end_sent_ = false;
};

}  // namespace av
