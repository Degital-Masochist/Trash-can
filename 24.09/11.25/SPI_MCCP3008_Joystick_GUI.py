import spidev
import time
import tkinter as tk
import threading

delay = 0.5

sw_channel = 0
vrx_channel = 1
vry_channel = 2

spi = spidev.SpiDev()

spi.open(0, 0)

spi.max_speed_hz = 100000

def readadc(adcnum):
	if adcnum > 7 or adcnum < 0:
		return -1
	r = spi.xfer2([1, 8 + adcnum << 4, 0])
	data = ((r[1] & 3) << 8) + r[2]
	return data

class JoystickApp:
	def __init__(self, master):
		self.master = master
		master.title("Joystick Monitor")
		
		self.x_label = tk.Label(master, text="X", font=("Helvetica", 16))
		self.x_label.pack()
		
		self.y_label = tk.Label(master, text="Y", font=("Helvetica", 16))
		self.y_label.pack()
		
		self.sw_label = tk.Label(master, text="Y", font=("Helvetica", 16))
		self.sw_label.pack()
		
		self.canvas = tk.Canvas(master, width=200, height=200, bg="white")
		self.canvas.pack(pady=20)
		
		self.joystick = self.canvas.create_oval(90, 90, 110, 110, fill="red")
		
		self.toggle_button  = tk.Button(master, text="Start", command=self.toggle_reading)
		self.toggle_button.pack(pady=10)
		
		self.is_reading = False
		self.read_thread = None
		
	def toggle_reading(self):
		if self.is_reading:
			self.stop_reading()
		else:
			self.start_reading()
			
	def start_reading(self):
		self.is_reading = True
		self.toggle_button.config(text="Stop")
		self.read_thread = threading.Thread(target=self.read_joystick)
		self.read_thread.start()
		
	def stop_reading(self):
		self.is_reading = False
		self.toggle_button.config(text="Start")
		if self.read_thread:
			self.read_thread.join()
			
	def read_joystick(self):
		while self.is_reading:
			vrx_pos = readadc(vrx_channel)
			vry_pos = readadc(vry_channel)
			sw_val = readadc(sw_channel)
			self.update_gui(vrx_pos, vry_pos, sw_val)
			time.sleep(0.1)
			
	def update_gui(self, x, y, sw):
		self.master.after(0, lambda: self.x_label.config(text=f"X: {x}"))
		self.master.after(0, lambda: self.y_label.config(text=f"X: {y}"))
		self.master.after(0, lambda: self.sw_label.config(text=f"X: {sw}"))
		self.master.after(0, lambda: self.update_joystick_position(x, y))
		
	def update_joystick_position(self, x, y):
		canvas_x = (x / 1023) * 200
		canvas_y = 200 - (y / 1023) * 200
		self.canvas.coords(self.joystick, canvas_x-10, canvas_y-10, canvas_x+10, canvas_y+10)
		
	def closing(self):
		self.stop_reading()
		spi.close()
		self.master.destroy()
		
def main():
	root = tk.Tk()
	app = JoystickApp(root)
	root.protocol("WM_DELETE_WINDOW", app.closing)
	root.mainloop()
	
if __name__ == "__main__":
	main()
