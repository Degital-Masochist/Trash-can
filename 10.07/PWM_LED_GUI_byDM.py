import RPi.GPIO as GPIO
import tkinter as tk
import threading
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)

pwm = GPIO.PWM(18, 50)
pwm.start(0)

class LEDControlApp:
	def __init__(self, master):
		self.master = master
		master.title("자동 pwm 제어")
		
		self.is_running = False
		self.current_duty = 0
		
		self.duty_label = tk.Label(master, text= "Duty Cycle:0%")
		self.duty_label.pack(pady=10)
		
		self.freq_label = tk.Label(master, text="pwm 주기: 20ms (50Hz)")
		self.freq_label.pack(pady=10)
		
		self.toggle_button = tk.Button(master, text="시작", command=self.toggle_pwm)
		self.toggle_button.pack(pady=20)
		
		self.quit_button = tk.Button(master, text="종료", command=self.quit)
		self.quit_button.pack(pady=20)
		
		self.pwm_thread = None
		
	def toggle_pwm(self):
		if self.is_running:
			self.is_running = False
			self.toggle_button.config(text="시작")
			
		else:
			self.is_running = True
			self.toggle_button.config(text="정지")
			self.pwm_thread = threading.Thread(target=self.run_pwm)
			self.pwm_thread.start()
			
	def run_pwm(self):
		while self.is_running:
			for dc in range(0, 101, 5):
				if not self.is_running:
					break
				self.update_pwm(dc)
				time.sleep(0.1)
				
			for dc in range(100, -1, -5):
				if not self.is_running:
					break
				self.update_pwm(dc)
				time.sleep(0.1)
				
	def update_pwm(self, dc):
		pwm.ChangeDutyCycle(dc)
		self.duty_label.config(text=f"Duty Cycle : {dc}%")
		if dc == 100:
			self.toggle_button.config(text="앙")
		else:
			self.toggle_button.config(text="정지")
		if dc == 0:
			self.quit_button.config(text="앙")
		else:
			self.quit_button.config(text="종료")

	def quit(self):
		GPIO.cleanup()
		self.master.quit()

def main():
	root= tk.Tk()
	app= LEDControlApp(root)
		
	try:
		root.mainloop()
	finally:
		app.quit()
			
if __name__ == "__main__":
	main()
