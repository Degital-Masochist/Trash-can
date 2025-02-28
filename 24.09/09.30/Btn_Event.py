import RPi.GPIO as GPIO
import time

BUTTON_PIN = 15
def button_pressed_callback(channel):
	print("button pushed!")
	
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING, callback=button_pressed_callback, bouncetime=200)
print("프로그램이 실행 중입니다. 버튼을 눌러보세요. 종료하려면 Ctrl+C를 누르세요.")
try:
	while True:
		time.sleep(0.1)
except KeyboardInterrupt:
	print("\n프로그램종료")
finally:
	GPIO.cleanup()
	print("GPIO가 정리되었습니다.")
