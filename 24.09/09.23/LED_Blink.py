import RPi.GPIO as GPIO
import time

led_pin = 4
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(led_pin, GPIO.OUT, initial=GPIO.LOW)

for i in range(10):
	GPIO.output(led_pin, GPIO.HIGH)
	time.sleep(1)
	GPIO.output(led_pin,0)
	time.sleep(1)
GPIO.cleanup()
