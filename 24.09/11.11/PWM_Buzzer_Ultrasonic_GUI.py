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
p = GPIO.PWM(18, 50)
p.start(0)
p.ChangeFrequency(523)

class distanceAlarmAPP:
	def __init__(self, master):
		self.master = master
		master.title("거리 측정 및 경보시스템")
		
		self.distance_label = tk.Label(master, text="거리: - cm", font=("Helvetica", 24))
		self.distance_label.pack(pady=20)		
		
		self.status_label = tk.Label(master, text="대기중", font=("Helvetica", 18))
		self.status_label.pack(pady=10)
		
		self.start_button = tk.Button(master, text="측정시작", command=self.toggle_measurement)
		self.start_button.pack(pady=10)
		
		self.is_measuring = False
		self.measurement_thread = None 
		
	def toggle_measurement(self):
		if self.is_measuring:
			self.stop_measurement()
		else:
			self.start_measurement()
			
	def start_measurement(self):
		self.is_measuring = True
		self.start_button.config(text="측정중지")
		self.measurement_thread = threading.Thread(target=self.measure_distance_loop)
		self.measurement_thread.start()
		
	def stop_measurement(self):
		self.is_measuring = False
		self.start_button.config(text="측정시작")
		if self.measurement_thread:
			self.measurement_thread.join()
		self.update_status("대기중")
		p.ChangeDutyCycle(0)
		
	def measure_distance_loop(self):
		while self.is_measuring:
			dist = self.measure_distance()
			self.update_distance(dist)
			if dist <= 50:
				self.update_status("물체 감지!")
				self.play_alarm()
			else:
				self.update_status("측정중")
				p.ChangeDutyCycle(0)
			time.sleep(0.1)
			
	def measure_distance(self):
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
		return distance
		
	def update_distance(self, dist):
		self.distance_label.config(text=f"거리: {dist:.1f} cm")
        
	def update_status(self, status):
		self.status_label.config(text=status)
		
	def play_alarm(self):
		Frq = [523, 587, 659, 698, 784]
		for fr in Frq:
			if not self.is_measuring:
				break
			p.ChangeFrequency(fr)
			p.ChangeDutyCycle(50)
			time.sleep(0.1)

	def quit(self):
		GPIO.cleanup()
		self.master.quit()
		
def main():
	root = tk.Tk()
	app = distanceAlarmAPP(root)
	root.protocol("WM_DELETE_WINDOW", app.quit)
	root.mainloop()
	
if __name__ == "__main__":
	main()
