from evdev import ecodes
import RPi.GPIO as GPIO
import joystick	#need window mode
import time

IN1 = 27
IN2 = 22
ENA = 17

IN3 = 20
IN4 = 21
ENB = 16

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)
GPIO.setup(ENB, GPIO.OUT)

GPIO.output(IN1, GPIO.LOW)
GPIO.output(IN2, GPIO.LOW)
GPIO.output(IN3, GPIO.LOW)
GPIO.output(IN4, GPIO.LOW)

p = GPIO.PWM(ENA, 1000)
p.start(0)

pp = GPIO.PWM(ENB, 1000)
pp.start(50)

def motor_f():
	print("motor forward")
	
def motor_off():
	print("motor off")
	
def key_input():
	x_val = 32768
	y_val = 32768
	west_val = 0
	l_val = 0
	r_val = 0
	select_val = 0
	start_val = 0
	Y_val = 0
	X_val = 0
	A_val = 0
	B_val = 0
	
	motor_state = None
	
	for event in gamepad.read_loop():
		if event.type == ecodes.EV_ABS and event.code == ecodes.ABS_X:
			x_val = event.value
			print(f"X axis: {x_val}")
			
		if event.type == ecodes.EV_ABS and event.code == ecodes.ABS_Y:
			y_val = event.value
			print(f"Y axis: {y_val}")
			
			if y_val < 32768:
				if motor_state != 'on':
					motor_state = 'on'
					motor_f()
			else:
				if motor_state != 'off':
					motor_state = 'off'
					motor_off()
			
		if event.type == ecodes.EV_KEY and event.code == ecodes.BTN_WEST:
			l_val = event.value
			print(f"L button: {l_val}")
			
		if event.type == ecodes.EV_KEY and event.code == ecodes.BTN_Z:
			r_val = event.value
			print(f"R button: {r_val}")
			
		if event.type == ecodes.EV_KEY and event.code == ecodes.BTN_TL:
			select_val = event.value
			print(f"Select button: {select_val}")
			
		if event.type == ecodes.EV_KEY and event.code == ecodes.BTN_TR:
			start_val = event.value
			print(f"Start button: {start_val}")
			
		if event.type == ecodes.EV_KEY and event.code == ecodes.BTN_C:
			Y_val = event.value
			print(f"Y button: {Y_val}")
			
		if event.type == ecodes.EV_KEY and event.code == ecodes.BTN_NORTH:
			X_val = event.value
			print(f"X button: {X_val}")
			
		if event.type == ecodes.EV_KEY and event.code == ecodes.BTN_EAST:
			A_val = event.value
			print(f"A button: {A_val}")
			
		if event.type == ecodes.EV_KEY and event.code == ecodes.BTN_SOUTH:
			B_val = event.value
			print(f"B button: {B_val}")

def main():
	global gamepad
	gamepad = joystick.gamepad
	key_input()
			
if __name__ == "__main__":
	main()
