#include <Arduino.h>
#include <kf1d.h>
#include <cfloat>

KF1D::KF1D(double Ts, double qa, double R)
    : _x(0.0),
      _v(0.0),
      _P00(1e3),
      _P01(0.0),
      _P10(0.0),
      _P11(1e3),
      _qa(qa),
      _R(R),
      _use_joseph_form(true),
      _gate_Nsigma(0.0) {
    this->set_Ts(Ts);
}

void KF1D::set_Ts(double Ts) {
    _F00 = 1.0;
    _F01 = Ts;
    _F10 = 0.0;
    _F11 = 1.0;

    _G0 = 0.5 * Ts * Ts;
    _G1 = Ts;

    _H0 = 1.0;
    _H1 = 0.0;

    this->_buildQ(Ts);
}

void KF1D::predict(double u) {
    // (x, v)^T = F * (x, v)^T + G * u
    double x_prev = _x;
    double v_prev = _v;

    _x = _F00 * x_prev + _F01 * v_prev + _G0 * u;
    _v = _F10 * x_prev + _F11 * v_prev + _G1 * u;

    // P = FPF^T + Q
    double FP00 = _F00 * _P00 + _F01 * _P10;
    double FP01 = _F00 * _P01 + _F01 * _P11;
    double FP10 = _F10 * _P00 + _F11 * _P10;
    double FP11 = _F10 * _P01 + _F11 * _P11;

    _P00 = FP00 * _F00 + FP01 * _F01 + _Q00;
    _P01 = FP00 * _F10 + FP01 * _F11 + _Q01;
    _P10 = FP10 * _F00 + FP11 * _F01 + _Q10;
    _P11 = FP10 * _F10 + FP11 * _F11 + _Q11;
}

bool KF1D::correct(double z, Com* com) {
    // Innovation : y = z - Hx
    double y = z - (_H0 * _x + _H1 * _v);  // Measurement residual

    // S = HPH^T + R
    double HP0 = _H0 * _P00 + _H1 * _P10;
    double HP1 = _H0 * _P01 + _H1 * _P11;
    double S = HP0 * _H0 + HP1 * _H1 + _R;  // Residual covariance
    if (S <= DBL_EPSILON && !isfinite(S))
        S = DBL_EPSILON;

    // Gate check
    if (_gate_Nsigma > 0.0) {
        double nsq = _gate_Nsigma * _gate_Nsigma;
        if ((y * y) > (nsq * S))
            return false;
    }

    // Kalman gain K = PH^T S^-1
    double K0 = (_P00 * _H0 + _P01 * _H1) / S;  // Kalman gain element 0
    double K1 = (_P10 * _H0 + _P11 * _H1) / S;  // Kalman gain element 1

    // Update state estimate
    _x += K0 * y;
    _v += K1 * y;

    // Update estimate covariance
    double I_KH_00 = 1.0 - K0 * _H0;
    double I_KH_01 = 0.0 - K0 * _H1;
    double I_KH_10 = 0.0 - K1 * _H0;
    double I_KH_11 = 1.0 - K1 * _H1;

    if (_use_joseph_form) {
        // Joseph form: P = (I - KH) P (I - KH)^T + KRK^T
        double T00 = I_KH_00 * _P00 + I_KH_01 * _P10;
        double T01 = I_KH_00 * _P01 + I_KH_01 * _P11;
        double T10 = I_KH_10 * _P00 + I_KH_11 * _P10;
        double T11 = I_KH_10 * _P01 + I_KH_11 * _P11;

        _P00 = T00 * I_KH_00 + T01 * I_KH_01 + K0 * _R * K0;
        _P01 = T00 * I_KH_10 + T01 * I_KH_11 + K0 * _R * K1;
        _P10 = T10 * I_KH_00 + T11 * I_KH_01 + K1 * _R * K0;
        _P11 = T10 * I_KH_10 + T11 * I_KH_11 + K1 * _R * K1;
    } else {
        // Standard form: P = (I - KH)P
        double P00_prev = _P00;
        double P01_prev = _P01;
        double P10_prev = _P10;
        double P11_prev = _P11;

        _P00 = I_KH_00 * P00_prev + I_KH_01 * P10_prev;
        _P01 = I_KH_00 * P01_prev + I_KH_01 * P11_prev;
        _P10 = I_KH_10 * P00_prev + I_KH_11 * P10_prev;
        _P11 = I_KH_10 * P01_prev + I_KH_11 * P11_prev;
    }

    if (com != nullptr) {
        String pValues = "P: " + String(_P00) + ", " + String(_P01) + ", " +
                         String(_P10) + ", " + String(_P11);
        com->print((char*)pValues.c_str());
    }
    return true;
}

void KF1D::reset(double x0, double v0) {
    _x = x0;
    _v = v0;

    _P00 = 1e3;
    _P01 = 0.0;
    _P10 = 0.0;
    _P11 = 1e3;
}

void KF1D::_buildQ(double Ts) {
    double Ts2 = Ts * Ts;
    double Ts3 = Ts2 * Ts;
    double Ts4 = Ts2 * Ts2;

    _Q00 = 0.25 * Ts4 * _qa;
    _Q01 = 0.5 * Ts3 * _qa;
    _Q10 = 0.5 * Ts3 * _qa;
    _Q11 = Ts2 * _qa;
}
