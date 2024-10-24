import RPi.GPIO as GPIO
import time
import tkinter as tk
from tkinter import messagebox

class LEDControlApp:
	def __init__(self, master):
		self.master = master
		master.title("LED Control")
		
		self.led_pin = 4
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.led_pin,GPIO.OUT)
		
		self.label = tk.Label(master, text="LED 깜빡임 횟수:")
		self.label.pack()
		
		self.entry = tk.Entry(master)
		self.entry.pack()
		
		self.start_button = tk.Button(master, text="시작", command=self.start_blinking)
		self.start_button.pack()
		
		self.quit_button = tk.Button(master, text="종료", command=self.quit)
		self.quit_button.pack()
	def start_blinking(self):
		try:
			blink_count = int(self.entry.get())
			
			if blink_count <= 0:
				raise ValueError
				
			for _ in range(blink_count):
				GPIO.output(self.led_pin, GPIO.HIGH)
				self.master.update()
				time.sleep(1)
				GPIO.output(self.led_pin, GPIO.LOW)
				self.master.update()
				time.sleep(1)
				
			messagebox.showinfo("완료", f"LED가 {blink_count}번 깜빡였습니다.")
		except ValueError:
			messagebox.showerror("오류" "유효한 숫자를 입력해 주세요.")
			
	def quit(self):
			GPIO.cleanup()
			self.master.quit()
if __name__ == "__main__":
	root  = tk.Tk()
	app = LEDControlApp(root)
	root.mainloop()
