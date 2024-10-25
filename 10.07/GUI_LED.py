import RPi.GPIO as GPIO
import tkinter as tk
import threading

button_pin = 15
led_pin = 4
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(led_pin, GPIO.OUT)

GPIO.output(led_pin, 0)
light_on = False

class LEDControlApp:
	def __init__(self, master):
		self.master = master
		master.title("LED 제어")
	
		self.label = tk.Label(master, text= "LED 상태: 꺼짐", font= ("Helvetica", 16))
		self.label.pack(pady=20)
	
		self.led_image = tk.Canvas(master, width=100, height=100)
		self.led_image.pack(pady=20)
		self.update_led_image()
	
		self.button = tk.Button(master, text="LED 상태 변경", command=self.toggle_led)
		self.button.pack(pady=20)
	
		GPIO.add_event_detect(button_pin, GPIO.RISING, callback=self.button_callback, bouncetime=300)
	
	def button_callback(self, channel):
		self.master.after(0, self.toggle_led)
    
	def toggle_led(self):
		global light_on
		light_on = not light_on
		GPIO.output(led_pin, int(light_on))
		self.update_led_status()
		
	def update_led_status(self):
		status = "켜짐" if light_on else "꺼짐"
		self.label.config(text=f"LED 상태: {status}")
		self.update_led_image()
		
	def update_led_image(self):
		self.led_image.delete("all")
		color = "yellow" if light_on else "gray"
		self.led_image.create_oval(10, 10, 90, 90, fill=color, outline="")
		
		
def main():
	root= tk.Tk()
	app= LEDControlApp(root)
		
	try:
		root.mainloop()
	finally:
		GPIO.cleanup()
			
if __name__ == "__main__":
	main()
