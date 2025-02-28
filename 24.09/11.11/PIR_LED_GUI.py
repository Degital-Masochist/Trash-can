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
		
	def toggle_measurement():
		try:
			pass
		except:
			pass
	
	def quit(self):
		GPIO.cleanup()
		self.master.quit()
		
def main():
	root = tk.Tk()
	app = PIRSensorApp(root)
	root.protocol("WM_DELETE_WINDOW", app.quit)
	root.mainloop()
	
if __name__ == "__main__":
	main()
