import RPi.GPIO as GPIO
import time

# Imposta il numero di pin secondo la numerazione BCM
GPIO.setmode(GPIO.BCM)

# Configura i GPIO 8 e 9
GPIO.setup(2, GPIO.OUT)  # GPIO 8 come output
GPIO.setup(3, GPIO.OUT)  # GPIO 9 come output per PWM


# # Imposta GPIO 8 su HIGH
GPIO.output(2, GPIO.LOW)
print("GPIO 2 impostato su HIGH")

# Imposta PWM su GPIO 9 con frequenza e duty cycle consigliati
pwm_freq = 50 # Frequenza PWM in Hz
duty_cycle = 50  # Duty cycle in percentuale
pwm = GPIO.PWM(3, pwm_freq)
pwm.start(duty_cycle)
print(f"PWM attivato su GPIO 9 con frequenza {pwm_freq}Hz e duty cycle {duty_cycle}%")

# Mantiene il PWM per 3 secondi
time.sleep(1)

# Ferma il PWM e imposta GPIO 8 su LOW
pwm.stop()
GPIO.output(2, GPIO.LOW)
print("PWM fermato su GPIO 9 e GPIO 8 impostato su LOW")

# Ripristina lo stato dei GPIO

