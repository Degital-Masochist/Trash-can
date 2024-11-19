import RPi.GPIO as GPIO
import tkinter as tk
import time
import threading

led_R = 20
led_Y = 21
sensor = 4

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(led_R, GPIO.OUT)
GPIO.setup(led_Y, GPIO.OUT)
GPIO.setup(sensor, GPIO.IN)

class PIRSensorApp:
	def __init__(self, master):	
		self.master = master
		master.title("PIR sensor monitoring")
	
		self.status_label = tk.Label(master, text="Ready", font=("Helvetica", 18))
		self.status_label.pack(pady=20)
	
		self.led_frame = tk.Frame(master)
		self.led_frame.pack(pady=10)
	
		self.yellow_led = tk.Canvas(self.led_frame, width=50, height=50, bg='gray')
		self.yellow_led.pack(side=tk.LEFT, padx=10)
	
		self.red_led = tk.Canvas(self.led_frame, width=50, height=50, bg='gray')
		self.red_led.pack(side=tk.LEFT, padx=10)
	
		self.start_button = tk.Button(master, text="Start", command=self.toggle_measurement)
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
		self.status_label.config(text="센서 준비중")
		self.master.after(1000, self.start_monitoring)
		
	def start_monitoring(self):
		self.status_label.config(text="모니터링중")
		self.measurement_thread = threading.Thread(target=self.monitor_sensor)
		self.measurement_thread.start()
		
	def stop_measurement(self):
		self.is_measuring = False
		self.start_button.config(text="측정 시작")
		self.status_label.config(text="대기중")
		if self.measurement_thread:
			self.measurement_thread.join()
		self.update_leds(False, False)
		
	def monitor_sensor(self):
		while self.is_measuring:
			if GPIO.input(sensor) == 1:
				self.update_status("동작 감지")
				self.update_leds(True, False)
			else:
				self.update_status("모니터링 중")
				self.update_leds(False, True)
			time.sleep(0.2)
			
	def update_status(self, message):
		self.master.after(0, lambda: self.status_label.config(text=message))
	
	def update_leds(self, yellow_on, red_on):
		self.master.after(0, lambda: self.yellow_led.config(bg='yellow' if yellow_on else 'gray'))
		self.master.after(0, lambda: self.red_led.config(bg='red' if red_on else 'gray'))
		GPIO.output(led_Y, yellow_on)
		GPIO.output(led_R, red_on)
	
	def quit(self):
		self.stop_measurement()
		GPIO.cleanup()
		self.master.quit()
		
def main():
	root = tk.Tk()
	app = PIRSensorApp(root)
	root.protocol("WM_DELETE_WINDOW", app.quit)
	root.mainloop()
	
if __name__ == "__main__":
	main()
