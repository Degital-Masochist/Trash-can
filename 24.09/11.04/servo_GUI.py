import RPi.GPIO as GPIO
import time
import tkinter as tk
import threading

SERVO_PIN = 18
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

servo = GPIO.PWM(SERVO_PIN, 50)
servo.start(0)

class servoapp:
	def __init__(self, master):
		self.master = master
		master.title("Servo controll APP")
		
		self.is_rotating = False
		self.current_angle = 0
		
		self.button_frame = tk.Frame(master)
		self.button_frame.pack(pady = 5)
		
		self.btn_cw = tk.Button(self.button_frame, text="시계 방향")
		self.btn_cw.pack(side=tk.LEFT, padx=5)
		self.btn_cw.bind('<ButtonPress>', lambda e: self.start_rotation('cw'))
		self.btn_cw.bind('<ButtonRelease>', self.stop_rotation)
		
		self.btn_ccw = tk.Button(self.button_frame, text="반시계 방향")
		self.btn_ccw.pack(side=tk.LEFT, padx=5)
		self.btn_ccw.bind('<ButtonPress>', lambda e: self.start_rotation('ccw'))
		self.btn_ccw.bind('<ButtonRelease>', self.stop_rotation)
		
		self.status_label = tk.Label(master, text = "노예 : 대기 중")
		self.status_label.pack(pady = 10)
		
	def angle_to_duty(self, angle):
		return (angle / 18) + 2.5
	
	def start_rotation(self, direction):
		self.is_rotating = True
		threading.Thread(target=self.rotate, args=(direction,)).start()
	
	def stop_rotation(self, event):
		self.is_rotating = False
		
	def rotate(self, direction):
		while self.is_rotating:
			if direction == 'cw':
				self.current_angle = (self.current_angle - 5) % 180
			else:
				self.current_angle = (self.current_angle + 5) % 180
			
			duty = self.angle_to_duty(self.current_angle)
			servo.ChangeDutyCycle(duty)
			self.master.after(0, self.update_status)
			time.sleep(0.1)
			
	def update_status(self):
		self.status_label.config(text=f"현재 각도: {self.current_angle}도")
		
	def quit(self):
		self.is_rotating = False
		servo.stop()
		GPIO.cleanup()
		self.master.quit()
		
def main():
	root = tk.Tk()
	app = servoapp(root)
	root.protocol("WM_DELETE_WINDOW", app.quit)
	root.geometry("800x600")
	root.mainloop()
	
if __name__ == "__main__":
	main()
