#ifndef PID_H
#define PID_H

/**
 * @brief Simple discrete-time PID controller helper class.
 *
 * This PID implementation is intended for use in a control loop where the
 * sample time (dt) is fixed or explicitly set via `setSampleTime`. The
 * controller integrates the error and computes a PID output on `compute()`.
 */
class PID {
   public:
    /**
     * @brief Construct a new PID controller
     *
     * @param kp Proportional gain
     * @param ki Integral gain
     * @param kd Derivative gain
     * @param dtSeconds Sample time in seconds (default 0.01s)
     *
     */
    PID(float kp, float ki, float kd, float dtSeconds = 0.01f);

    /**
     * @brief Compute the PID output for the provided error value.
     *
     * This method should be called at a fixed interval matching `dtSeconds`.
     *
     * @param error The current error (setpoint - measurement)
     * @return float The controller output (unclamped).
     */
    float compute(float error);

    /**
     * @brief Reset the internal integrator and history (previous error).
     */
    void reset();

    /**
     * @brief Update PID tunings.
     *
     * @param kp Proportional gain
     * @param ki Integral gain
     * @param kd Derivative gain
     */
    void setTunings(float kp, float ki, float kd);

    /**
     * @brief Set the sample time for the controller.
     *
     * @param dtSeconds Sample time in seconds
     */
    void setSampleTime(float dtSeconds);

   private:
    float _kp;             // Proportional gain
    float _ki;             // Integral gain
    float _kd;             // Derivative gain
    float _dtSeconds;      // Sample time in seconds
    float _integral;       // Integral accumulator
    float _previousError;  // Previous error for derivative term
};

#endif
