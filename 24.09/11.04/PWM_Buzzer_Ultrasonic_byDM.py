import RPi.GPIO as GPIO
import time

TRIG = 23
ECHO = 24

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)
GPIO.setup(18, GPIO.OUT)
pwm = GPIO.PWM(18, 50)
pwm.start(0)
pwm.ChangeFrequency(523)

try:
	while True:
		GPIO.output(TRIG, True)
		time.sleep(0.00001)
		GPIO.output(TRIG, False)
		
		while GPIO.input(ECHO)==0:
			start = time.time()
		while GPIO.input(ECHO)==1:
			stop = time.time()
		
		check_time = stop - start
		distance = check_time * 34300 / 2
		
		print("Distance : %.i cm" % distance)
		
		if distance <= 50:
			print("Alert!")
			pwm.ChangeDutyCycle(20)
			time.sleep(0.1)
			pwm.ChangeDutyCycle(0)
			
		time.sleep(0.1)
	
except KeyboardInterrupt:
	print("Measurement stopped by User")
	GPIO.cleanup()
