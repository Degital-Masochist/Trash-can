import spidev
import time
import tkinter as tk
import threading

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 100000

ldr_channel = 0

def readadc(adcnum):
	if adcnum > 7 or adcnum < 0:
		return -1
	r = spi.xfer2([1, 8 + adcnum << 4, 0])
	data = ((r[1] & 3) << 8) + r[2]
	return data
	
class LDRApp:
	def __init__(self, master):
		self.master = master
		master.title("LDR Sensor monitor")
		
		self.value_label = tk.Label(master, text="LDR Value: 0", font=("Helvetica", 16))
		self.value_label.pack(pady=10)
		
		self.canvas = tk.Canvas(master, width=400, height=200, bg="white")
		self.canvas.pack(pady=10)
		
		self.toggle_button  = tk.Button(master, text="Start", command=self.toggle_reading)
		self.toggle_button.pack(pady=10)
		
		self.is_reading = False
		self.read_thread = None
		self.data_points = []
		
	def toggle_reading(self):
		if self.is_reading:
			self.stop_reading()
		else:
			self.start_reading()
			
	def start_reading(self):
		self.is_reading = True
		self.toggle_button.config(text="Stop")
		self.read_thread = threading.Thread(target=self.read_ldr)
		self.read_thread.start()
		
	def stop_reading(self):
		self.is_reading = False
		self.toggle_button.config(text="Start")
		if self.read_thread:
			self.read_thread.join()
			
	def read_ldr(self):
		while self.is_reading:
			ldr_value = readadc(ldr_channel)
			self.update_gui(ldr_value)
			time.sleep(0.5)
			
	def update_gui(self, value):
		self.master.after(0, lambda: self.value_label.config(text=f"LDR Value: {value}"))
		self.master.after(0, lambda: self.update_graph(value))
		
	def update_graph(self, value):
		self.data_points.append(value)
		if len(self.data_points) > 50:
			self.data_points.pop(0)
			
		self.canvas.delete("all")
		width = 400
		height = 200
		if len(self.data_points) > 1:
			x_step = width / (len(self.data_points) - 1)
			y_scale = height / 1024
		
		
			for i in range(1, len(self.data_points)):
				x1 = (i - 1) * x_step
				y1 = height - self.data_points[i-1] * y_scale
				x2 = i * x_step
				y2 = height - self.data_points[i] * y_scale
				self.canvas.create_line(x1, y1, x2, y2, fill="blue")
		elif len(self.data_points) == 1:
			x = width / 2
			y = height - self.data_points[0] * (height / 1024)
			self.canvas.create_oval(x-2, y-2, x+2, y+2, fill="blue")
			
	def closing(self):
		self.stop_reading()
		spi.close
		self.master.destroy()
		
def main():
	root = tk.Tk()
	app = LDRApp(root)
	root.protocol("WM_DELETE_WINDOW", app.closing)
	root.mainloop()
	
if __name__ == "__main__":
	main()
