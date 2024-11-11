import RPi.GPIO as GPIO
import time
import tkinter as tk
import threading

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

class DistanceApp:
	def __init__(self, master):
		self.master = master
		master.title("Distance")
		
		self.distance_label = tk.Label(master, text="Distance: - cm", font=("Helvetica", 24))
		self.distance_label.pack(pady=20)
		
		self.status_label = tk.Label(master, text="Ready")
		self.status_label.pack(pady=10)
		
		self.toggle_button = tk.Button(master, text= "측정 시작", command=self.toggle_measurement)
		self.toggle_button.pack(pady=10)
		
		self.is_measuring = False
		self.measurement_thread = None
		
	def toggle_measurement(self):
		if self.is_measuring:
			self.stop_measurement()
		else:
			self.start_measurement()
			
	def start_measurement(self):
		self.is_measuring = True
		self.toggle_button.config(text="측정 중지")
		self.measurement_thread = threading.Thread(target=self.measure_distance)
		self.measurement_thread.start()
		self.status_label.config(text="측정 중")
		
	def stop_measurement(self):
		self.is_measuring = False
		self.toggle_button.config(text="측정 시작")
		self.status_label.config(text="대기 중")
		if self.measurement_thread:
			self.measurement_thread.join()
			
	def measure_distance(self):
		while self.is_measuring:
			GPIO.output(TRIG, False)
			time.sleep(0.1)
			
			GPIO.output(TRIG, True)
			time.sleep(0.00001)
			GPIO.output(TRIG, False)
			
			while GPIO.input(ECHO) == 0:
				pulse_start = time.time()
				
			while GPIO.input(ECHO) == 1:
				pulse_end = time.time()
				
			pulse_duration = pulse_end - pulse_start
			distance = pulse_duration * 34300 / 2
			self.update_distance(distance)
			time.sleep(0.1)
			
			if distance <= 50:
				self.status_label.config(text="Alert!")
				pwm.ChangeDutyCycle(20)
				time.sleep(0.1)
				pwm.ChangeDutyCycle(0)
				time.sleep(0.1)
				self.status_label.config(text="측정 중")
			
	def update_distance(self, distance):
		self.master.after(0, lambda: self.distance_label.config(text=f"거리 : {distance:.1f} cm"))
		
	def quit(self):
		self.stop_measurement()
		GPIO.cleanup()
		self.master.quit()
		self.pwm.stop()
		
def main():
	root = tk.Tk()
	app = DistanceApp(root)
	root.protocol("WM_DELETE_WINDOW", app.quit)
	root.mainloop()
	
if __name__ == "__main__":
	main()
