import RPi.GPIO as GPIO
import tkinter as tk
from tkinter import ttk
import threading

BUTTON_PIN = 15
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

class PushButtonApp:
	def __init__(self, master):
		self.master = master
		master.title("PUSH 버튼 모니터")
		
		self.label = ttk.Label(master, text="버튼 상태: 대기중")
		self.label.pack(pady=20)
		
		self.count_label = ttk.Label(master, text="버튼 누른 횟수:0")
		self.count_label.pack(pady=10)
		
		self.quit_button = ttk.Button(master, text="종료", command=self.quit)
		self.quit_button.pack(pady=10)
		
		self.button_count = 0
		self.is_running = True
		
		GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING, callback=self.button_pressed_callback, bouncetime=200)
		
		self.monitor_thread = threading.Thread(target=self.monitor_gpio)
		self.monitor_thread.start()
		
		def button_pressed_callback(self, channel):
			self.button_count = +1
			self.master.after(0, self.update_gui)
			
		def update_gui(self):
			self.label.config(text="버튼 상태: 눌림")
			self.count_label.config(text=f"버튼 누른 횟수: {self.button_count}")
			self.master.after(200, self.reset_label)
			
		def reset_label(self):
			self.label.config(text="버튼상태: 대기중")
			
		def monitor_gpio(self):
			while self.is_running:
				self.master.update()
				
		def quit(self):
			self.is_running = False
			GPIO.cleanup()
			self.master.quit()
			
if __name__ == "__main__":
	root = tk.Tk()
	app = PushButtonApp(root)
	root.protocol("WM_DELETE_WINDOW", app.quit)
	root.mainloop()
