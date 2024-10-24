import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)

scale=[262, 294, 330, 349, 392, 440, 494, 523]
	   #도   레    미    파    솔    라    시    도^
#scale=[392, 392, 440, 440, 393, 393, 330, 392, 392, 330, 330, 294]
try:
	p = GPIO.PWM(12, 100)
	p.start(10)
	
	for freq in scale:
		p.ChangeFrequency(freq)
		time.sleep(0.5)
		
except KeyboardInterrupt:
	print("Program stoped by user")
	
except Exception as e:
	print(f"Error : {e}")
	
finally:
	if p is not None:
		p.stop()
		del p
		
	GPIO.cleanup()
	print("GPIO DELETE.")
	
print("Program stop")
