import RPi.GPIO as GPIO
import time
import tkinter as tk
import threading

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)

scale=[262, 294, 330, 349, 392, 440, 494, 523]
note_names = ['도', '레', '미', '파', '솔', '라', '시', '도']

class ScalePlayerApp:
	def __init__(self, master):
		self.master = master
		master.title("PIANO")
		
		self.p = GPIO.PWM(12, 100)
		self.is_running = False
		
		self.play_button = tk.Button(master, text="PLAY", command=self.play_scale)
		self.play_button.pack(pady=10)
		
		self.note_frame = tk.Frame(master)
		self.note_frame.pack(pady=5)
		self.note_buttons = []
		
		for i, note in enumerate(note_names):
			btn = tk.Button(self.note_frame, text=note, command=lambda i=i: self.play_note(i))
			btn.pack(side=tk.LEFT, padx=2)
			self.note_buttons.append(btn)
			
		self.status_label = tk.Label(master, text="Ready")
		self.status_label.pack(pady=10)
		
	def play_scale(self):
		try:
			pass
		finally:
			pass
		
def main():
	root = tk.Tk()
	app = ScalePlayerApp(root)
	root.mainloop()
			
if __name__ == "__main__":
	main()
