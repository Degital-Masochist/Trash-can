import RPi.GPIO as GPIO
import time
import tkinter as tk
import threading

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)

scale=[262, 294, 330, 349, 392, 440, 494, 523, 1]
scale_expanded = [1, 130.8128, 138.5913, 146.8324, 155.5635, 164.8138, 174.6141, 184.9972, 195.9977, 207.6523, 220, 233.0819, 246.9417, 
261.6256, 277.1826, 293.6648, 311.1270, 329.6276, 349.2282, 369.9944, 391.9954, 415.3047, 440, 466.1638, 493.8833, 523.2511]
note_names = ['Do', 'Re', 'Mi', 'Fa', 'Sol', 'Ra', 'Ti', 'Do^']
main_menu = ['Scale', 'School bell', 'Classic']
stop_menu = ['Stop', 'EXIT']
School_bell = list(scale[i] for i in (4, 4, 5, 5, 4, 4, 2, 8, 4, 4, 2, 2, 1, 8, 4, 4, 5, 5, 4, 4, 2, 8, 4, 2, 1, 2))
Classic = list(scale_expanded[i] for i in (
10, 14, 10, 14, 10, 14, 10, 14, 10, 14, 10, 14,
12, 15, 12, 15, 12, 15, 12, 15, 12, 15, 12, 15,
14, 17, 14, 17, 14, 17, 14, 16, 14, 16, 14, 16,
12, 15, 17, 15, 18, 17, 15, 14, 12, 2, 14, 12,
17, 14, 17, 18, 17, 14, 12, 12,
15, 14, 12, 15, 17, 20, 18, 17,
15, 12, 14, 15, 12, 14, 9, 9,
15, 17, 18, 20, 18, 17, 15,
17, 9, 12, 15, 9, 12, 9, 17, 18,
20, 17, 18, 17, 17, 18, 20, 18, 17, 20,
19, 19, 20, 14, 17, 18, 20, 18, 17
))
scale_note = [262, 294, 330, 349, 392, 440, 494, 523]

class ScalePlayerApp:
	def __init__(self, master):
		self.master = master
		master.title("Harmony")
		
		self.pwm = GPIO.PWM(12, 50)
		self.is_running = False
		self.iis_running = False
		self.iiis_running = False
		self.scale_running = False

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
			btn = tk.Button(self.note_frame, text=note, command=lambda i=i: self.doremi(i))
			btn.pack(side=tk.LEFT, padx=2)
			self.note_buttons.append(btn)
			
		self.stop_frame = tk.Frame(master)
		self.stop_frame.pack(pady=5)
		self.stop_buttons = []

		for i, stop1 in enumerate(stop_menu):
			btn = tk.Button(self.stop_frame, text = stop1, command = lambda i = i: self.stop_btn(i))
			btn.pack(side = tk.LEFT, padx = 2)
			self.stop_buttons.append(btn)
			
		self.status_label = tk.Label(master, text="노예(대학원생) : 노는 중")
		self.status_label.pack(pady=10)

	def see_main(self, i):
		if i == 0:
			self.toggle_scale()
		elif i == 1:
			self.toggle_School_bell()
		elif i == 2:
			self.toggle_Classic()
		
	def toggle_scale(self):
		if self.is_running:
			self.is_running = False
			self.status_label.config(text="노예(대학원생) : 노는 중")
			
		else:
			self.is_running = True
			self.status_label.config(text="노예(대학원생) : 갈려나가는 중")
			threading.Thread(target=self.play_scale).start()
		
	def toggle_School_bell(self):
		if self.iis_running:
			self.iis_running = False
			self.status_label.config(text="노예(대학원생) : 노는 중")

		else:
			self.iis_running = True
			self.status_label.config(text="노예(대학원생) : 갈려나가는 중")
			threading.Thread(target=self.play_School_bell).start()

	def toggle_Classic(self):
		if self.iiis_running:
			self.iiis_running = False
			self.status_label.config(text="노예(대학원생) : 노는 중")

		else:
			self.iiis_running = True
			self.status_label.config(text="노예(대학원생) : 갈려나가는 중")
			threading.Thread(target=self.play_Classic).start()

	def play_scale(self):
		self.is_running = True
		self.pwm.start(20)
		for i in scale:
			if not self.is_running:
				break
			self.pwm.ChangeDutyCycle(20)
			self.pwm.ChangeFrequency(i)
			time.sleep(0.3)
			self.pwm.ChangeDutyCycle(0)
			time.sleep(0.05)
		self.pwm.stop()
		self.is_running = False
		self.status_label.config(text="노예(대학원생) : 노는 중")

	def play_School_bell(self):
		self.iis_running = True
		self.pwm.start(20)
		for i in School_bell:
			if not self.iis_running:
				break
			elif i == 8:
				self.pwm.ChangeDutyCycle(0)
				time.sleep(0.1)
			else:
				self.pwm.ChangeDutyCycle(20)
				self.pwm.ChangeFrequency(i)
				time.sleep(0.5)
				self.pwm.ChangeDutyCycle(0)
				time.sleep(0.05)
		self.pwm.stop()
		self.iis_running = False
		self.status_label.config(text="노예(대학원생) : 노는 중")

	def play_Classic(self):
		self.iiis_running = True
		self.pwm.start(20)
		for i in Classic:
			if not self.iiis_running:
				break
			self.pwm.ChangeDutyCycle(20)
			self.pwm.ChangeFrequency(i)
			time.sleep(0.3)
			self.pwm.ChangeDutyCycle(0)
			time.sleep(0.05)
		self.pwm.stop()
		self.iis_running = False
		self.status_label.config(text="노예(대학원생) : 노는 중")

	def quit(self):
		self.is_running = False
		self.iis_running = False
		self.iiis_running = False
		self.pwm.stop()
		GPIO.cleanup()
		self.master.destroy()

	def doremi(self, scale_note):
		if self.scale_running:
			self.scale_running = False
			self.status_label.config(text="노예(대학원생) : 노는 중")

		else:
			self.scale_running = True
			self.status_label.config(text="노예(대학원생) : 갈려나가는 중")
			threading.Thread(target=self.run_doremi, args=(scale_note,)).start()

	def run_doremi(self, scale_note):
		self.scale_running = True
		self.pwm.start(20)
		freq = scale[scale_note]
		self.pwm.ChangeFrequency(freq)
		time.sleep(0.5)
		self.pwm.stop()
		self.scale_running = False
		self.status_label.config(text="노예(대학원생) : 노는 중")

	def stop_btn(self, i):
		if i == 0:
			self.status_label.config(text="노예(대학원생) : 앙")
			self.scale_running = False
			self.is_running = False
			self.iis_running = False
			self.iiis_running = False
			self.pwm.ChangeDutyCycle(0)
			self.pwm.stop()
			self.status_label.config(text="노예(대학원생) : 노는 중")
		elif i == 1:
			quit()
		
def main():
	root = tk.Tk()
	app = ScalePlayerApp(root)
	root.protocol("WM_DELETE_WINDOW", app.quit)
	root.mainloop()
			
if __name__ == "__main__":
	main()
