#ifndef KF1D_H
#define KF1D_H

#include <Arduino.h>

/**
 * @brief 1D Kalman filter
 *
 */
class KF1D {
   public:
    /**
     * @brief Initialize the 1D Kalman filter state
     *
     * @param Ts Sampling time (s)
     * @param qa Acceleration noise magnitude (m^2/s^4)
     * @param R Measurement noise covariance (m^2)
     */
    KF1D(double Ts, double qa, double R);
    ~KF1D() = default;

    /**
     * @brief Set the sampling time for the 1D Kalman filter
     *
     * @param Ts Sampling time (s)
     *
     */
    void set_Ts(double Ts);

    /**
     * @brief Predict the next state of the 1D Kalman filter
     *
     * @param u Control input (acceleration) (m/s^2)
     *
     */
    void predict(double u);

    /**
     * @brief Correct the state estimate of the 1D Kalman filter with a new
     * measurement
     *
     * @param z Measurement (position) (m)
     * @return true If the measurement is within the validation gate
     * @return false If the measurement is outside the validation gate
     */
    bool correct(double z);

   private:
    double _x;  // State estimate (m)
    double _v;  // State velocity (m/s)

    double _P00, _P01, _P10, _P11;  // Estimate covariance matrix elements

    double _F00, _F01, _F10, _F11;  // State transition matrix elements
    double _G0, _G1;                // Control input matrix elements
    double _H0, _H1;                // Measurement matrix elements

    double _Q00, _Q01, _Q10, _Q11;  // Process noise covariance matrix elements
    double _qa;                     // Acceleration noise magnitude (m^2/s^4)
    double _R;                      // Measurement noise covariance (m^2)

    bool _use_joseph_form;  // Flag to use Joseph form for covariance update
    double _gate_Nsigma;    // Validation gate size in standard deviations

    /**
     * @brief Build the process noise covariance matrix Q based on the sampling
     * time
     *
     * @param Ts Sampling time (s)
     */
    void _buildQ(double Ts);
};

#endif  // KF1D_H
