from evdev import ecodes
import RPi.GPIO as GPIO
import joystick	#need windows mode
import threading
import time

IN1 = 3
IN2 = 4
ENA = 2

IN3 = 15
IN4 = 18
ENB = 14

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)
GPIO.setup(ENB, GPIO.OUT)

GPIO.output(IN1, GPIO.HIGH)
GPIO.output(IN2, GPIO.HIGH)
GPIO.output(IN3, GPIO.HIGH)
GPIO.output(IN4, GPIO.HIGH)

p = GPIO.PWM(ENA, 1000)
p.start(0)

pp = GPIO.PWM(ENB, 1000)
pp.start(0)

def speed(p_value, pp_value):
	p.ChangeDutyCycle(p_value)
	pp.ChangeDutyCycle(pp_value)


def motor_forward():
	print("motor forward")
	GPIO.output(IN1, GPIO.HIGH)
	GPIO.output(IN2, GPIO.LOW)
	GPIO.output(IN3, GPIO.HIGH)
	GPIO.output(IN4, GPIO.LOW)
	speed(100, 100)
	
def motor_backward():
	print("motor backward")
	GPIO.output(IN1, GPIO.LOW)
	GPIO.output(IN2, GPIO.HIGH)
	GPIO.output(IN3, GPIO.LOW)
	GPIO.output(IN4, GPIO.HIGH)
	speed(100, 100)
	
def motor_left():
	print("motor left")
	GPIO.output(IN1, GPIO.HIGH)
	GPIO.output(IN2, GPIO.LOW)
	GPIO.output(IN3, GPIO.HIGH)
	GPIO.output(IN4, GPIO.LOW)
	speed(0, 100)
	
def motor_right():
	print("motor right")
	GPIO.output(IN1, GPIO.HIGH)
	GPIO.output(IN2, GPIO.LOW)
	GPIO.output(IN3, GPIO.HIGH)
	GPIO.output(IN4, GPIO.LOW)
	speed(100, 0)
	
def motor_forward_left():
	print("motor forward left")
	GPIO.output(IN1, GPIO.HIGH)
	GPIO.output(IN2, GPIO.LOW)
	GPIO.output(IN3, GPIO.HIGH)
	GPIO.output(IN4, GPIO.LOW)
	speed(50, 100)

def motor_forward_right():
	print("motor forward right")
	GPIO.output(IN1, GPIO.HIGH)
	GPIO.output(IN2, GPIO.LOW)
	GPIO.output(IN3, GPIO.HIGH)
	GPIO.output(IN4, GPIO.LOW)
	speed(100, 50)
	
def motor_backward_left():
	print("motor backward left")
	GPIO.output(IN1, GPIO.LOW)
	GPIO.output(IN2, GPIO.HIGH)
	GPIO.output(IN3, GPIO.LOW)
	GPIO.output(IN4, GPIO.HIGH)
	speed(50, 100)
	
def motor_backward_right():
	print("motor backward right")
	GPIO.output(IN1, GPIO.LOW)
	GPIO.output(IN2, GPIO.HIGH)
	GPIO.output(IN3, GPIO.LOW)
	GPIO.output(IN4, GPIO.HIGH)
	speed(100, 50)
	
def motor_off():
	print("motor off")
	GPIO.output(IN1, GPIO.HIGH)
	GPIO.output(IN2, GPIO.HIGH)
	GPIO.output(IN3, GPIO.HIGH)
	GPIO.output(IN4, GPIO.HIGH)
	speed(0, 0)
	
def key_input():	#Joystick Key
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
	
	motor_state = 'off'
	
	for event in gamepad.read_loop():	#Key Reaction
		if event.type == ecodes.EV_ABS and event.code == ecodes.ABS_X:
			x_val = event.value
			print(f"X axis: {x_val}")
			
			if x_val < 32768:
				if y_val < 32768:
					motor_forward_left()
				elif y_val > 32768:
					motor_backward_left()
				else:
					motor_left()
					
			elif x_val > 32768:
				if y_val < 32768:
					motor_forward_right()
				elif y_val > 32768:
					motor_backward_right()
				else:
					motor_right()
					
			else:
				motor_off()
			
		if event.type == ecodes.EV_ABS and event.code == ecodes.ABS_Y:
			y_val = event.value
			print(f"Y axis: {y_val}")
			
			if y_val < 32768:
				if x_val < 32768:
					motor_forward_left()
				elif x_val > 32768:
					motor_forward_right()
				else:
					motor_forward()
					
			elif y_val >32768:
				if x_val < 32768:
					motor_backward_left()
				elif x_val > 32768:
					motor_backward_right()
				else:
					motor_backward()
					
			else:
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
	threading.Thread(target = key_input).start()
			
if __name__ == "__main__":
	main()
