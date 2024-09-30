import RPi.GPIO as GPIO
import tkinter as tk
import threading
import time

class ButtonMonitorApp:
	def __init__(self, master):
		self.master = master
		master.title("Button Monitor")
		
		self.button_pin = 15
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
		
		self.status_label = tk.Label(master, text="버튼상태: 대기중")
		self.status_label.pack(pady=20)
		
		self.quit_button = tk.Button(master, text="종료", command=self.quit)
		self.quit_button.pack(pady=10)
		
		self.is_running = True
		self.monitor_thread = threading.Thread(target=self.monitor_button)
		self.monitor_thread.start()
		
	def monitor_button(self):	
		last_state = GPIO.input(self.button_pin)
		while self.is_running:
			current_state = GPIO.input(self.button_pin)
			if current_state != last_state:
				if current_state == 1: #GPIO.HIGH:
					self.update_status("버튼이 눌렸습니다!")
				else:
					self.update_status("버튼이 떼어졌습니다.")
				last_state = current_state
			time.sleep(0.1)
			
	def update_status(self, message):
		self.master.after(0, self.status_label.config, {"text": message})
		
	def quit(self):
		self.is_running = False
		self.monitor_thread.join()
		GPIO.cleanup()
		self.master.quit()
		
if __name__ == "__main__":
	root = tk.Tk()
	app = ButtonMonitorApp(root)
	root.mainloop()
