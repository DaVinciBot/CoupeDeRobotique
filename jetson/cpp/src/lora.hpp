#pragma once
// Bidirectional LoRa over a transparent UART module (POSIX termios).
// Mirrors python/src/lora/lora.py: latest-wins TX, line-buffered RX, handler dispatch.

#include <atomic>
#include <condition_variable>
#include <functional>
#include <mutex>
#include <string>
#include <thread>
#include <unordered_map>
#include <vector>

namespace av {

class LoRa {
public:
    using HandlerFn = std::function<void(const std::vector<std::string>&)>;

    // dummy=true: no serial I/O; queue_send just logs (DUMMY_LORA mode).
    LoRa(std::string port, int baud, bool dummy = false,
         double min_send_interval = 1.0 / 15.0, int tx_error_threshold = 5);
    ~LoRa();

    bool connect();          // open the port; false on failure
    bool is_healthy() const;
    void start();            // launch TX/RX threads
    void stop();             // stop threads
    void disconnect();       // stop + close port

    void queue_send(const std::string& data);          // latest-wins
    void register_handler(int cmd_num, HandlerFn fn);   // RX dispatch

private:
    void send_loop();
    void recv_loop();
    void dispatch(const std::string& line);

    std::string port_;
    int baud_;
    bool dummy_;
    double min_send_interval_;
    int tx_error_threshold_;

    int fd_ = -1;
    std::atomic<bool> healthy_{false};
    std::atomic<int> tx_errors_{0};

    std::mutex data_mutex_;
    std::condition_variable data_cv_;
    std::string pending_;
    bool has_pending_ = false;

    std::atomic<bool> stop_{false};
    std::thread tx_thread_;
    std::thread rx_thread_;
    std::string rx_buffer_;

    std::mutex handlers_mutex_;
    std::unordered_map<int, HandlerFn> handlers_;
};

}  // namespace av
