import RPi.GPIO as GPIO
import time

IN1 = 27
IN2 = 22
ENA = 17

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

GPIO.output(IN1, GPIO.HIGH)
GPIO.output(IN2, GPIO.LOW)

p = GPIO.PWM(ENA, 1000)
p.start(0)

try:
	for d in range(1, 101, 1):
		p.ChangeDutyCycle(d)
		print("ld:{}%".format(d))
		time.sleep(0.03)
	print("st1 e")
	
	p.ChangeDutyCycle(0)
	time.sleep(2)
	print("st2")
	
	GPIO.output(IN1, GPIO.LOW)
	GPIO.output(IN2, GPIO.HIGH)
	p.ChangeDutyCycle(50)
	time.sleep(2)
	print("st3")
	
finally:
	p.stop()
	GPIO.cleanup()
