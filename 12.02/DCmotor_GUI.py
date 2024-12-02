import RPi.GPIO as GPIO
import time
import tkinter as tk
import threading

GPIO.setmode(GPIO.BCM)
StepPins = [12, 16, 20, 21]

for pin in StepPins:
	GPIO.setup(pin, GPIO.OUT)
	GPIO.output(pin, False)
	
StepCount = 4

Seq = [	[0, 0, 0, 1],
[0, 0, 1, 0],
[0, 1, 0, 0],
[1, 0, 0, 0]]

class DCApp:
	def __init__(self, master):
		self.master = master
		master.title("Step Motor Controll")
		
		self.is_running = False
		self.direction = 1
		self.speed = 0.001
		
		self.main_frame = tk.Frame(master)
		self.main_frame.pack(pady = 10)
		
		self.btn_1 = tk.Button(self.main_frame, text = "CW", command=lambda: self.set_direction(1))
		self.btn_1.pack(side = tk.LEFT, padx = 2)
		
		self.btn_2 = tk.Button(self.main_frame, text = "CCW", command=lambda: self.set_direction(-1))
		self.btn_2.pack(side = tk.LEFT, padx = 2)
		
		self.btn_stop = tk.Button(master, text="Start", command=self.toggle_motor)
		self.btn_stop.pack(pady = 10)
		
		self.speed_slider = tk.Scale(master, from_=1, to=100, orient=tk.HORIZONTAL, label="SPEED", command=self.update_speed)
				
		self.speed_slider.set(50)
		self.speed_slider.pack(pady = 0)
		
		self.status_label = tk.Label(master, text="Status : Stop")
		self.status_label.pack(pady = 10)
		
		self.motor_thread = None
		
	def set_direction(self, dir):
		self.direction = dir
		self.update_direction_buttons()
		
	def update_direction_buttons(self):
		if self.direction == 1:
			self.btn_1.config(relief=tk.SUNKEN)
			self.btn_2.config(relief=tk.RAISED)
		else:
			self.btn_1.config(relief=tk.RAISED)
			self.btn_2.config(relief=tk.SUNKEN)
			
	def toggle_motor(self):
		if self.is_running:
			self.stop_motor()
		else:
			self.start_motor()
			
	def start_motor(self):
		self.is_running = True
		self.btn_stop.config(text="Stop")
		self.status_label.config(text="Status : RUNNING")
		self.motor_thread = threading.Thread(target=self.run_motor)
		self.motor_thread.start()
		
	def stop_motor(self):
		self.is_running = False
		self.btn_stop.config(text="Start")
		self.status_label.config(text="Status : Stop")
		if self.motor_thread:
			self.motor_thread.join()
		
	def update_speed(self, value):
		self.speed = (101 - int(value)) / 10000
		
	def run_motor(self):
		step_counter = 0
		while self.is_running:
			for pin in range(4):
				xpin = StepPins[pin]
				if Seq[step_counter][pin] != 0:
					GPIO.output(xpin, True)
				else:
					GPIO.output(xpin, False)
					
			step_counter += self.direction
			
			if step_counter >= StepCount:
				step_counter = 0
			if step_counter < 0:
				step_counter = StepCount - 1
				
			time.sleep(self.speed)

	def close():
		self.stop_motor()
		GPIO.cleanup()
		self.master.quit()

def main():
	root = tk.Tk()
	app = DCApp(root)
	root.protocol("WM_DELETE_WINDOW", app.close)
	root.mainloop()
	
if __name__ == "__main__":
	main()
