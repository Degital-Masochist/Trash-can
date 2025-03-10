import picamera2
import pyaudio
import speech_recognition as sr
import time
import threading
import os
from PIL import Image, ImageTk
import numpy as np

class CameraApp:
	def __init__(self):
		self.camera = None
		
		try:
			self.camera = picamera2.Picamera2()
			self.camera.start_preview()
			self.camera.configure(self.camera.create_still_configuration())
		except Exception as e:
			print(f"Camera initialization failed: {e}")
			self.camera = None

	def start_camera_preview(self):
		while self.running:
			image_array = self.camera.capture_array()
			image = Image.fromarray(image_array)
			yield image

	def stop_camera_preview(self):
		self.camera.stop_preview()

	def take_picture(self):
		usb_dir = self.find_usb_mount_point()
		
		if usb_dir:
			gallery_dir = os.path.join(usb_dir, "Gallery")
			if not os.path.exists(gallery_dir):
				os.makedirs(gallery_dir)
				
			filename = f"{time.strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
			filepath = os.path.join(gallery_dir, filename)
			self.camera.capture(filepath)
			print(f"Picture taken and saved as {filename} USB.")
		
		else:
			local_gallery = os.path.join(os.getcwd(), "Gallery")
			if not os.path.exists(local_gallery):
				os.makedirs(local_gallery)
				
			filename = f"{time.strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
			filepath = os.path.join(local_gallery, filename)
			self.camera.capture(filepath)
			print(f"Picture taken and saved as {filename} locally.")
			
	def find_usb_mount_point(self):
		possible_dirs = ["/media/pi", "/media", "/mnt"]
		
		for base in possible_dirs:
			if os.path.exists(base):
				for entry in os.listdir(base):
					candidate = os.path.join(base, entry)
					if os.path.ismount(candidate):
						return candidate
		return None

	def quit(self):
		self.running = False
		self.camera.close()
		print("LOOP EXIT")

def main():
	app = CameraApp()
	
if __name__ == "__main__":
	main()
