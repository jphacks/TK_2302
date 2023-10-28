# app/pigpio_config.py

import pigpio

SERVO_PIN = 18
pi = pigpio.pi()

def set_servo_angle(angle):
    assert 0 <= angle <= 180, '角度は0から180の間に注意する'
    pulse_width = (angle / 180) * (2500 - 500) + 500
    pi.set_servo_pulsewidth(SERVO_PIN, pulse_width)
