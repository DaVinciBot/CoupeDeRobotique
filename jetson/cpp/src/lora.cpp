#include "lora.hpp"

#include <cerrno>
#include <chrono>
#include <cstdio>
#include <cstring>
#include <sstream>

#include <fcntl.h>
#include <termios.h>
#include <unistd.h>

namespace av {

namespace {

// Map a numeric baud to its termios speed_t constant.
speed_t baud_const(int baud) {
    switch (baud) {
        case 9600:   return B9600;
        case 19200:  return B19200;
        case 38400:  return B38400;
        case 57600:  return B57600;
        case 115200: return B115200;
        case 230400: return B230400;
        default:     return B115200;
    }
}

}  // namespace

LoRa::LoRa(std::string port, int baud, bool dummy,
           double min_send_interval, int tx_error_threshold)
    : port_(std::move(port)),
      baud_(baud),
      dummy_(dummy),
      min_send_interval_(min_send_interval),
      tx_error_threshold_(tx_error_threshold) {}

LoRa::~LoRa() { disconnect(); }

bool LoRa::connect() {
    if (dummy_) {
        healthy_ = true;
        std::printf("LoRa: DUMMY mode (no serial I/O)\n");
        return true;
    }

    fd_ = ::open(port_.c_str(), O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (fd_ < 0) {
        std::printf("LoRa: cannot open %s: %s\n", port_.c_str(), std::strerror(errno));
        return false;
    }

    termios tty{};
    if (tcgetattr(fd_, &tty) != 0) {
        std::printf("LoRa: tcgetattr failed: %s\n", std::strerror(errno));
        ::close(fd_);
        fd_ = -1;
        return false;
    }

    speed_t spd = baud_const(baud_);
    cfsetispeed(&tty, spd);
    cfsetospeed(&tty, spd);

    cfmakeraw(&tty);                  // 8N1, no flow control, raw mode
    tty.c_cflag |= (CLOCAL | CREAD);  // ignore modem lines, enable receiver
    tty.c_cflag &= ~CRTSCTS;          // no hardware flow control
    tty.c_cc[VMIN] = 0;               // non-blocking read
    tty.c_cc[VTIME] = 0;

    if (tcsetattr(fd_, TCSANOW, &tty) != 0) {
        std::printf("LoRa: tcsetattr failed: %s\n", std::strerror(errno));
        ::close(fd_);
        fd_ = -1;
        return false;
    }

    tcflush(fd_, TCIOFLUSH);
    // Purge stray bytes from the DTR/RTS reset by sending an empty line.
    const char nl = '\n';
    (void)::write(fd_, &nl, 1);
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    tcflush(fd_, TCIFLUSH);

    healthy_ = true;
    tx_errors_ = 0;
    std::printf("LoRa connected on %s @ %d baud\n", port_.c_str(), baud_);
    return true;
}

bool LoRa::is_healthy() const {
    return healthy_ && (dummy_ || fd_ >= 0);
}

void LoRa::start() {
    stop_ = false;
    if (dummy_) return;  // nothing to pump in dummy mode
    if (!tx_thread_.joinable())
        tx_thread_ = std::thread(&LoRa::send_loop, this);
    if (!rx_thread_.joinable())
        rx_thread_ = std::thread(&LoRa::recv_loop, this);
}

void LoRa::stop() {
    stop_ = true;
    data_cv_.notify_all();
    if (tx_thread_.joinable()) tx_thread_.join();
    if (rx_thread_.joinable()) rx_thread_.join();
}

void LoRa::disconnect() {
    stop();
    if (fd_ >= 0) {
        ::close(fd_);
        fd_ = -1;
    }
    healthy_ = false;
}

void LoRa::queue_send(const std::string& data) {
    if (dummy_) {
        std::string s = data;
        if (!s.empty() && s.back() == '\n') s.pop_back();
        std::printf("[DUMMY_LORA] %s\n", s.c_str());
        return;
    }
    {
        std::lock_guard<std::mutex> lk(data_mutex_);
        pending_ = data;
        has_pending_ = true;
    }
    data_cv_.notify_one();
}

void LoRa::register_handler(int cmd_num, HandlerFn fn) {
    std::lock_guard<std::mutex> lk(handlers_mutex_);
    handlers_[cmd_num] = std::move(fn);
}

void LoRa::send_loop() {
    while (!stop_) {
        std::string data;
        {
            std::unique_lock<std::mutex> lk(data_mutex_);
            data_cv_.wait_for(lk, std::chrono::milliseconds(500),
                              [&] { return has_pending_ || stop_; });
            if (stop_) break;
            if (!has_pending_) continue;
            data = pending_;
            has_pending_ = false;
        }
        if (data.empty()) continue;
        if (data.back() != '\n') data += '\n';

        ssize_t n = ::write(fd_, data.data(), data.size());
        if (n < 0) {
            int e = ++tx_errors_;
            std::printf("LoRa TX error (%d): %s\n", e, std::strerror(errno));
            if (e >= tx_error_threshold_) {
                healthy_ = false;
                std::printf("LoRa TX degraded: module likely disconnected\n");
            }
            continue;
        }
        tx_errors_ = 0;
        // Pace by wire time + minimum interval (matches Python throttle).
        double wire_time = static_cast<double>(data.size()) * 10.0 / baud_;
        auto ms = std::chrono::duration<double>(wire_time + min_send_interval_);
        std::this_thread::sleep_for(
            std::chrono::duration_cast<std::chrono::milliseconds>(ms));
    }
}

void LoRa::recv_loop() {
    char buf[256];
    while (!stop_) {
        ssize_t n = ::read(fd_, buf, sizeof(buf));
        if (n > 0) {
            rx_buffer_.append(buf, static_cast<size_t>(n));
            size_t pos;
            while ((pos = rx_buffer_.find('\n')) != std::string::npos) {
                std::string line = rx_buffer_.substr(0, pos);
                rx_buffer_.erase(0, pos + 1);
                dispatch(line);
            }
        } else {
            std::this_thread::sleep_for(std::chrono::milliseconds(20));
        }
    }
}

void LoRa::dispatch(const std::string& raw_line) {
    std::string line = raw_line;
    // strip CR/whitespace
    while (!line.empty() && (line.back() == '\r' || line.back() == ' '))
        line.pop_back();
    if (line.empty()) return;

    std::vector<std::string> parts;
    std::stringstream ss(line);
    std::string tok;
    while (std::getline(ss, tok, '|')) parts.push_back(tok);
    if (parts.empty()) return;

    int cmd;
    try {
        cmd = std::stoi(parts[0]);
    } catch (...) {
        std::printf("LoRa RX: frame without valid command number: '%s'\n",
                    line.c_str());
        return;
    }

    HandlerFn handler;
    {
        std::lock_guard<std::mutex> lk(handlers_mutex_);
        auto it = handlers_.find(cmd);
        if (it == handlers_.end()) {
            std::printf("LoRa RX: cmd %d unhandled\n", cmd);
            return;
        }
        handler = it->second;
    }
    std::vector<std::string> args(parts.begin() + 1, parts.end());
    try {
        handler(args);
    } catch (const std::exception& e) {
        std::printf("LoRa RX: handler cmd %d threw: %s\n", cmd, e.what());
    }
}

}  // namespace av
