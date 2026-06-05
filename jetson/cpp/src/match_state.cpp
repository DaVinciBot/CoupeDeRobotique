#include "match_state.hpp"

#include <algorithm>
#include <cmath>
#include <cstdio>

#include "arena.hpp"

namespace av {

using Clock = std::chrono::steady_clock;

namespace {
double secs_since(Clock::time_point t) {
    return std::chrono::duration<double>(Clock::now() - t).count();
}
}  // namespace

int MatchState::register_pami() {
    std::lock_guard<std::mutex> lk(m_);
    int pid = next_pami_id_++;
    pami_ids_.push_back(pid);
    return pid;
}

std::vector<int> MatchState::pami_ids() const {
    std::lock_guard<std::mutex> lk(m_);
    return pami_ids_;
}

bool MatchState::start_match(const std::string& color) {
    std::lock_guard<std::mutex> lk(m_);
    if (match_started_) return false;
    if (color != "B" && color != "Y") {
        std::printf("MatchState: unknown color '%s', expected 'B' or 'Y'\n",
                    color.c_str());
        return false;
    }
    team_color_ = color;
    match_started_ = true;
    start_ts_ = Clock::now();
    return true;
}

bool MatchState::match_started() const {
    std::lock_guard<std::mutex> lk(m_);
    return match_started_;
}

std::string MatchState::team_color() const {
    std::lock_guard<std::mutex> lk(m_);
    return team_color_;
}

double MatchState::elapsed() const {
    std::lock_guard<std::mutex> lk(m_);
    if (!match_started_) return 0.0;
    return secs_since(start_ts_);
}

bool MatchState::is_over() const {
    std::lock_guard<std::mutex> lk(m_);
    if (!match_started_) return false;
    return secs_since(start_ts_) >= MATCH_DURATION;
}

bool MatchState::should_send_pre_end() const {
    std::lock_guard<std::mutex> lk(m_);
    if (!match_started_ || pre_end_sent_) return false;
    return secs_since(start_ts_) >= (MATCH_DURATION - PRE_END_OFFSET);
}

void MatchState::mark_pre_end_sent() {
    std::lock_guard<std::mutex> lk(m_);
    pre_end_sent_ = true;
}

std::vector<std::tuple<int, double, double>>
MatchState::compute_depot_assignments() const {
    std::string color;
    std::vector<int> ids;
    {
        std::lock_guard<std::mutex> lk(m_);
        color = team_color_;
        ids = pami_ids_;
    }
    std::vector<std::tuple<int, double, double>> out;
    if (color.empty() || ids.empty()) return out;

    const auto& start =
        (color == "B") ? arena::start_blue : arena::start_yellow;

    // Sort depots by distance from the team's start-zone corner (matches Python).
    std::vector<arena::Zone> depots = arena::zone_depot;
    std::stable_sort(depots.begin(), depots.end(),
                     [&](const arena::Zone& a, const arena::Zone& b) {
                         double da = std::hypot(a.x - start.x, a.y - start.y);
                         double db = std::hypot(b.x - start.x, b.y - start.y);
                         return da < db;
                     });

    std::size_t n = std::min(ids.size(), depots.size());
    for (std::size_t i = 0; i < n; ++i) {
        out.emplace_back(ids[i], depots[i].x, depots[i].y);
    }
    return out;
}

std::string MatchState::build_msg_3(
    const std::vector<std::tuple<int, double, double>>& assignments) {
    std::string s = "3";
    char buf[64];
    for (const auto& a : assignments) {
        std::snprintf(buf, sizeof(buf), "|%d|%.3f|%.3f",
                      std::get<0>(a), std::get<1>(a), std::get<2>(a));
        s += buf;
    }
    s += "\n";
    return s;
}

}  // namespace av
