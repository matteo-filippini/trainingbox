import RPi.GPIO as GPIO
import time
from training import RewardGPIO

test = RewardGPIO(mode=1)
test.pwm_freq = 500
test.deliver(1)