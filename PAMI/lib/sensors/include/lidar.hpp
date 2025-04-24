#pragma once
#include <vector>

struct Gs2Point {
    float distance_mm;
    float angle_rad;
};

struct Gs2Object {
    float avgDistance;
    float avgAngle;
    float xGlob;
    float yGlob;
};

class Gs2Lidar {
public:
    void begin();                 
    void task();                  
    const std::vector<Gs2Object>& getObjects() const;

private:
    void processPacket(const uint8_t* p);
    std::vector<Gs2Object> objects_;
};
