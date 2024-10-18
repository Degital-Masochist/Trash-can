import RPi.GPIO as GPIO
import time
import tkinter as tk
import threading

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)

scale=[262, 294, 330, 349, 392, 440, 494, 523]
note_names = ['Do', 'Re', 'Mi', 'Fa', 'Sol', 'La', 'Ti', 'Do^']
main_menu = ['Scale', 'School bell', 'Siren']
School_bell = list(scale[i] for i in (5, 5, 6, 6, 5, 5, 3, 5, 5, 3 ,3, 2, 5, 5, 6, 6, 5, 5, 3, 5, 3, 2, 3, 1))


class ScalePlayerApp:
	def __init__(self, master):
		self.master = master
		master.title("PIANO")
		
		self.pwm = GPIO.PWM(12, 100)
		self.is_running = False

		self.main_frame = tk.Frame(master)
		self.main_frame.pack(pady=5)
		self.main_buttons = []
		
		for i, main in enumerate(main_menu):
			main_button = tk.Button(self.main_frame, text=main, command=lambda i=i: self.see_main(i))
			main_button.pack(side=tk.LEFT, padx=2)
			self.main_buttons.append(main_button)
		
		self.note_frame = tk.Frame(master)
		self.note_frame.pack(pady=5)
		self.note_buttons = []
		
		for i, note in enumerate(note_names):
			btn = tk.Button(self.note_frame, text=note, command=lambda i=i: self.play_note(i))
			btn.pack(side=tk.LEFT, padx=2)
			self.note_buttons.append(btn)
			
		self.status_label = tk.Label(master, text="State : Ready")
		self.status_label.pack(pady=10)
		
	def toggle_scale(self):
		if self.is_running:
			self.is_running = False
			self.status_label.config(text="State : Ready")
			
		else:
			self.is_running = True
			self.status_label.config(text="State : Running")
		
	def toggle_School_bell(self):
		if self.is_running:
			self.is_running = False
			self.status_label.config(text="State : Ready")

		else:
			self.is_running = True
			self.status_label.config(text="State : Running")

	def toggle_Siren(self):
		if self.is_running:
			self.is_running = False
			self.status_label.config(text="State : Ready")

		else:
			self.is_running = True
			self.status_label.config(text="State : Running")

	def play_scale(self):
		self.is_running = True
		self.pwm.start(10)
		for i in scale:
			if not self.is_running:
				break
			self.pwm.ChangeFrequence(i)
			time.sleep(0.2)
		self.pwm.stop()

	def play_School_bell(self):
		self.is_running = True
		self.pwm.start(10)
		for i in School_bell:
			if not self.is_running:
				break
			self.pwm.ChangeFrequence(i)
			time.sleep(0.2)

	def play_siren(self):
		self.is_running = True
		self.pwm.start(10)
		for i in (300, 750, 5):
			if not self.is_running:
				break
			self.pwm.ChangeFrequence(i)
			time.sleep(0.2)
		
def main():
	root = tk.Tk()
	app = ScalePlayerApp(root)
	root.mainloop()
			
if __name__ == "__main__":
	main()

# 음계재생옆 아이콘 하나 더 만들기(학교종 출력), 누르면 음성 나오게 코딩
