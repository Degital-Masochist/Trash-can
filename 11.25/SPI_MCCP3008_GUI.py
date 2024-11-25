import spidev
import time
import tkinter as tk
import threading

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

pot_channel = 0

def readadc(adcnum):
	if adcnum > 7 or adcnum < 0:
		return -1
	r = spi.xfer2([1, 8 + adcnum << 4, 0])
	data = ((r[1] & 3) << 8) + r[2]
	return data
	
class ADCReaderApp:
	def __init__(self, master):
		self.master = master
		master.title("ADC Voltage")
		
		self.value_label = tk.Label(master, text="ADC Value: ", font=("Helvetica", 16))
		self.value_label.pack(pady=10)
		
		self.voltage_label = tk.Label(master, text="Volt: ", font=("Helvetica", 16))
		self.voltage_label.pack(pady=10)
		
		self.toggle_button = tk.Button(master, text="Start", command=self.toggle_reading)
		self.toggle_button.pack(pady=20)
		
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
		self.read_thread = threading.Thread(target=self.read_adc)
		self.read_thread.start()
		
	def stop_reading(self):
		self.is_reading = False
		self.toggle_button.config(text="Start")
		if self.read_thread:
			self.read_thread.join()
			
	def read_adc(self):
		while self.is_reading:
			value = readadc(pot_channel)
			voltage = value * (3.3 / 1023.0)
			self.update_labels(value, voltage)
			time.sleep(0.5)
			
	def update_labels(self, value, voltage):
		self.value_label.config(text=f"ADC Value: {value}")
		self.voltage_label.config(text=f"Volt: {voltage:.2f}V")
			
	def closing():
		self.stop_reading()
		spi.close()
		self.master.destroy()
		
def main():
	root = tk.Tk()
	app = ADCReaderApp(root)
	root.protocol("WM_DELETE_WINDOW", app.closing)
	root.mainloop()
	
if __name__ == "__main__":
	main()
		
	
