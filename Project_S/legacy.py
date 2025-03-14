# car welcome sound, speed feedback, AI speaker(command : siri), servo motor(with button), 
# camera(command : siri, take a shot)

import os
import time
import camera
import pygame
import random
import threading
import tkinter as tk
import RPi.GPIO as GPIO
import speech_recognition as sr
from PIL import Image, ImageTk
from gps_speed import GPSReader
from concurrent.futures import TimeoutError

SERVO_PIN = 2
BUTTON_PIN = 3

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

s = GPIO.PWM(SERVO_PIN, 50)
s.start(0)

def set_angle(angle):
	duty = 2.5 + (angle / 18.0)
	s.ChangeDutyCycle(duty)
	time.sleep(0.3)
	s.ChangeDutyCycle(0)
	
def find_usb_soundscript_path():
	potential_bases = []
	if os.path.exists("/media/pi"):
		potential_bases.append("/media/pi")
	potential_bases.append("/media")
	for base in potential_bases:
		for root, dirs, _ in os.walk(base):
			if "SoundScript" in dirs:
				return os.path.join(root, "SoundScript")
	return None

class servoapp:
	def __init__(self, master, camera_app):
		self.master = master
		master.title("Dev Console")
		
		self.CameraApp = camera_app
		self.camera_available = self.CameraApp.camera is not None
		
		if self.camera_available:
			try:
				self.CameraApp.camera.start()
				camera_status = "ON"
				camera_status_color = "green"
			except Exception as e:
				print("Camera error:", e)
		else:
			camera_status = "OFF"
			camera_status_color = "red"

		self.btn_frame = tk.Frame(master)
		self.btn_frame.pack(pady = 5)

		self.btn_0 = tk.Button(self.btn_frame, text = "0", command = self.go_0)
		self.btn_0.pack(side = tk.LEFT, padx = 5)

		self.btn_90 = tk.Button(self.btn_frame, text = "90", command = self.go_90)
		self.btn_90.pack(side = tk.LEFT, padx = 5)

		self.btn_test = tk.Button(self.btn_frame, text = "BUTTON", command = self.button_action)
		self.btn_test.pack(side = tk.LEFT, padx = 5)
		
		self.btn_welcome = tk.Button(self.btn_frame, text = "Welcome", command = self.play_random_music)
		self.btn_welcome.pack(side = tk.LEFT, padx = 5)
		
		self.btn_camera = tk.Button(self.btn_frame, text = "Camera Preview", command = self.toggle_camera_preview)
		self.btn_camera.pack(pady = 10)

		self.status_label = tk.Label(master, text = "Ready")
		self.status_label.pack(pady = 10)
		
		self.addon_frame = tk.Frame(master)
		self.addon_frame.pack(pady = 20)
		
		self.welcome = tk.Label(self.addon_frame, text = "Welcome sound")
		self.welcome.pack(side = tk.LEFT, padx = 1)
		
		self.addon_welcome = tk.Label(self.addon_frame, text = "ON", fg = 'green')
		self.addon_welcome.pack(side = tk.LEFT, padx = 10)
		
		self.camera1 = tk.Label(self.addon_frame, text = "Camera")
		self.camera1.pack(side = tk.LEFT, padx = 1)
		
		self.addon_camera = tk.Label(self.addon_frame, text = camera_status, fg = camera_status_color)
		self.addon_camera.pack(side = tk.LEFT, padx = 10)
		
		self.turbo = tk.Label(self.addon_frame, text = "Turbo sound")
		self.turbo.pack(side = tk.LEFT, padx = 1)
		
		self.addon_turbo = tk.Label(self.addon_frame, text = "ON", fg = 'green')
		self.addon_turbo.pack(side = tk.LEFT, padx = 10)
		
		if not pygame.mixer.get_init():
			pygame.mixer.init()
		
		if self.camera_available:
			self.CameraApp.camera_frame = tk.Label(master, width = 900, height = 300)
			self.CameraApp.camera_frame.pack()
		else:
			self.CameraApp.camera_frame = None
		
		self.preview_active = False
		self.camera_thread = None
		self.voice_running = True

		threading.Thread(target = self.gpio_button_detect).start()
		self.turbo_sound_isExist()
		self.start()
		
	def toggle_camera_preview(self):
		if self.CameraApp.camera_frame is None:
			return
			
		if not self.preview_active:
			self.btn_camera.config(text = "Stop Preview")
			self.CameraApp.camera_frame.pack()
			self.update_preview()
		else:
			self.btn_camera.config(text = "Camera Preview")
			self.preview_active = False
			self.CameraApp.camera_frame.config(image = None)
			self.CameraApp.camera_frame.image = None
			self.CameraApp.camera_frame.pack_forget()
			
	def update_preview(self):
		def capture_image():
			try:
				frame = self.CameraApp.camera.capture_array()
				frame_image = Image.fromarray(frame)
				frame_image = frame_image.resize((self.CameraApp.camera_frame.winfo_width(), self.CameraApp.camera_frame.winfo_height()))
				tk_image = ImageTk.PhotoImage(frame_image)
				self.CameraApp.camera_frame.config(image = tk_image)
				self.CameraApp.camera_frame.image = tk_image
				
			except Exception as e:
				print(f"Error in capture_image: {e}")
						
			if self.preview_active:
					self.master.after(5, capture_image)
			
		if not self.preview_active:
			self.preview_active = True
			self.master.after(5, capture_image)

	def go_0(self):
		threading.Thread(target = self.go_0_start).start()

	def go_0_start(self):
		self.status_label.config(text = "Going Down")
		set_angle(0)
		self.status_label.config(text = "Ready")

	def go_90(self):
		threading.Thread(target = self.go_90_start).start()
	
	def go_90_start(self):
		self.status_label.config(text = "Going Up")
		set_angle(90)
		self.status_label.config(text = "Ready")

	def start(self):
		threading.Thread(target = self.go_0_start).start()
		threading.Thread(target = self.play_random_music).start()

	def play_random_music(self):
		start_soundscript = find_usb_soundscript_path()
		if start_soundscript is None:
			self.addon_welcome.config(text = "OFF", fg = 'red')
			return
			
		music_dir = os.path.join(start_soundscript, "Start")
		music_files = []
		
		for root, _, files in os.walk(music_dir):
			for file in files:
				if file.endswith('.mp3'):
					music_files.append(os.path.join(root, file))

		if not music_files:
			self.addon_welcome.config(text = "OFF", fg = 'red')
			return

		random_music = random.choice(music_files)
		pygame.mixer.music.load(random_music)
		pygame.mixer.music.play()

	def button_action(self):
		self.status_label.config(text = "Button action")
		threading.Thread(target = self.button_action_thread).start()
		
	def button_action_thread(self):
		set_angle(90)
		set_angle(0)
		self.status_label.config(text = "Ready")

	def gpio_button_detect(self):
		GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=self.button_detected, bouncetime=200)

	def button_detected(self, channel):
		self.button_action()
			
	def find_usb_microphone(self, p):
		for i in range(p.get_device_count()):
			info = p.get_device_info_by_index(i)
			if "USB" in info["name"]:
				return i
		return None
			
	def turbo_sound(self):
		turbo_soundscript = find_usb_soundscript_path()
		turbo_soundfile = os.path.join(turbo_soundscript, "Turbo")
		if os.path.exists(turbo_soundfile):
			pygame.mixer.music.load(turbo_soundfile)
			pygame.mixer.music.play()
		else:
			print("NO sound file")
			
	def turbo_sound_isExist(self):
		turbo_soundscript = find_usb_soundscript_path()
		if turbo_soundscript is not None:
			turbo_dir = os.path.join(turbo_soundscript, "Turbo")
			if os.path.exists(turbo_dir):
				mp3_found = False
				for root, dirs, files in os.walk(turbo_dir):
					for file in files:
						if file.lower().endswith('.mp3'):
							mp3_found = True
							break
					if mp3_found:
						break
				if mp3_found:
					self.addon_turbo.config(text = "ON", fg = "green")
				else:
					self.addon_turbo.config(text = "OFF", fg = "red")
			else:
				self.addon_turbo.config(text = "OFF", fg = "red")
		else:
			self.addon_turbo.config(text = "OFF", fg = "red")
			
	def quit(self):
		self.status_label.config(text = "STOP COMMAND DETECTED")
		s.stop()
		self.voice_running = False
		GPIO.cleanup()
		self.master.destroy()

def main():
	root = tk.Tk()
	camera_app = camera.CameraApp()
	app = servoapp(root, camera_app)
	root.protocol("WM_DELETE_WINDOW", app.quit)
	root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
	root.mainloop()

if __name__ == "__main__":
	main()
