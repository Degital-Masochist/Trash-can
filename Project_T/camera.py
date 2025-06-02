import tkinter as tk
import threading
from PIL import Image, ImageTk
import time
import libcamera
from picamera2 import Picamera2
import cv2
import numpy as np
from ultralytics import YOLO
from flask import Flask, Response, render_template_string

app = Flask(__name__)

output_frame = None
frame_lock = threading.Lock()
running = True

class CameraApp:
	def __init__(self, master):
		self.master = master
		master.title("YOLOv8 Person Detect System")

		self.picam2 =Picamera2()
		self.picam2.configure(self.picam2.create_preview_configuration(
			main={"size": (1024, 768)},
			transform=libcamera.Transform(hflip=True, vflip=True)))
		self.picam2.start()

		self.preview_label = tk.Label(master)
		self.preview_label.pack()

		self.model = YOLO("yolov8n.pt")

		self.photo = None
		self.running = True

		self.thread = threading.Thread(target=self.process_frames)
		self.thread.daemon = True
		self.thread.start()

		self.update_gui()

	def process_frames(self):
		global output_frame
		while self.running:
			frame = self.picam2.capture_array()
			frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
			results = self.model.predict(frame_bgr, verbose=False)[0]

			boxes = results.boxes.xyxy.cpu().numpy()
			classes = results.boxes.cls.cpu().numpy().astype(int)
			confidences = results.boxes.conf.cpu().numpy()

			for box, cls, conf in zip(boxes, classes, confidences):
				if cls == 0 and conf > 0.5:
					x1, y1, x2, y2 = map(int, box)
					label = f"Person {conf * 100:.1f}%"
					cv2.rectangle(frame_bgr, (x1, y1), (x2, y2), (0, 0, 255), 2)
					cv2.putText(frame_bgr, label, (x1, y1 - 10),
								cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

			with frame_lock:
				output_frame = frame_bgr.copy()

			frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
			img = Image.fromarray(frame_rgb)
			self.photo = ImageTk.PhotoImage(img)

			time.sleep(0.03)

	def update_gui(self):
		if self.photo:
			self.preview_label.config(image=self.photo)
			self.preview_label.image = self.photo
		if self.running:
			self.master.after(25, self.update_gui)

	def quit(self):
		self.running = False
		self.picam2.stop()
		self.master.destroy()

@app.route('/')
def index():
	return render_template_string("""
		<html>
		<head><title>YOLOv8 Person Detection Stream</title></head>
		<body>
			<h1>YOLOv8 Person Detection</h1>
			<img src="{{ url_for('video_feed') }}" style= "max-width : 100%; height : auto;">
		</body>
		</html>
	""")

def generate_stream():
	global output_frame
	while running:
		with frame_lock:
			if output_frame is None:
				continue
			ret, buffer = cv2.imencode('.jpg', output_frame)
			frame_bytes = buffer.tobytes()
		yield (b'--frame\r\n'
			   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
		time.sleep(0.05)

@app.route('/video_feed')
def video_feed():
	return Response(generate_stream(),
					mimetype='multipart/x-mixed-replace; boundary=frame')

def start_flask():
	app.run(host='0.0.0.0', port=1557, threaded=True)

def main():
	global running
	root = tk.Tk()
	camera_app = CameraApp(root)

	flask_thread = threading.Thread(target=start_flask)
	flask_thread.daemon = True
	flask_thread.start()

	def on_closing():
		global running
		running = False
		camera_app.running= False
		camera_app.quit()

	root.protocol("WM_DELETE_WINDOW", on_closing)
	root.mainloop()

if __name__ == "__main__":
	main()
