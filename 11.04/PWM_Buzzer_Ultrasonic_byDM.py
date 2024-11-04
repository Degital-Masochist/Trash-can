import RPi.GPIO as GPIO
import time

TRIG = 23
ECHO = 24

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)
GPIO.setup(12, GPIO.OUT)
pwm = GPIO.PWM(12, 50)
pwm.start(10)

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
		
		print("Distance : %.if cm" % distance)
		
		if distance <= 50:
			print("Alert!")
			pwm.ChangeFrequence(523)
			time.sleep(0.05)
			pwm.ChangeFrequence(0)
			
		time.sleep(0.1)
	
except KeyboardInterrupt:
	print("Measurement stopped by User")
	GPIO.cleanup()