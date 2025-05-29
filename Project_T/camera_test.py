import tkinter as tk
import picamera2
import threading
import libcamera
import time
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
from PIL import Image, ImageTk

class CameraApp:
	def __init__(self, master):
		self.master = master
		master.title("Camera")
		
		self.c = picamera2.Picamera2()
		self.c.configure(self.c.create_preview_configuration(main={"size": (640, 480)}, transform=libcamera.Transform(hflip=True, vflip=True)))
		self.c.start()

		self.c_frame = tk.Label(master)
		self.c_frame.pack(pady=10)
		
		self.update_preview()

	def start_monitoring(self):
		self.status_label.config(text="MONITORING")
		self.measurement_thread = threading.Thread(target=self.monitor_sensor)
		self.measurement_thread.start
		
	def update_preview(self):
		def capture_image():
			frame = self.c.capture_array()
			frame_image = Image.fromarray(frame)
			tk_image = ImageTk.PhotoImage(frame_image)
			self.c_frame.config(image=tk_image)
			self.c_frame.image = tk_image
			self.master.after(5, self.update_preview)
			
		thread = threading.Thread(target=capture_image)
		thread.start()
		
	def quit(self):
		self.c.stop()
		self.master.destroy()
		
def main():
	root = tk.Tk()
	app = CameraApp(root)
	root.protocol("WM_DELETE_WINDOW", app.quit)
	root.mainloop()
	
if __name__ == "__main__":
	main()
