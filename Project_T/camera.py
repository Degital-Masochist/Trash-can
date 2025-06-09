import cv2
import libcamera
from picamera2 import Picamera2
import numpy as np
from ultralytics import YOLO
import threading
import time

class CaptureThread(threading.Thread):
    def __init__(self, picam2):
        super().__init__()
        self.picam2 = picam2
        self.frame = None
        self.stopped = False
        self.lock = threading.Lock()

    def run(self):
        while not self.stopped:
            frame = self.picam2.capture_array()
            with self.lock:
                self.frame = frame

    def read(self):
        with self.lock:
            return self.frame.copy() if self.frame is not None else None

    def stop(self):
        self.stopped = True

class InferenceThread(threading.Thread):
    def __init__(self, capture_thread, model, fps):
        super().__init__()
        self.capture_thread = capture_thread
        self.model = model
        self.stopped = False
        self.fps = fps
        self.frame_interval = 1.0 / fps

    def run(self):
        last_time = time.time()
        while not self.stopped:
            current_time = time.time()
            elapsed = current_time - last_time
            if elapsed < self.frame_interval:
                time.sleep(self.frame_interval - elapsed)
            last_time = time.time()

            frame = self.capture_thread.read()
            if frame is None:
                continue

            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            results = self.model.predict(frame_bgr, imgsz=320, verbose=False, conf=0.5)[0]

            boxes = results.boxes
            xyxy = boxes.xyxy.cpu().numpy()
            cls = boxes.cls.cpu().numpy().astype(int)
            conf = boxes.conf.cpu().numpy()

            for box, class_id, confidence in zip(xyxy, cls, conf):
                if class_id == 0 and confidence > 0.5:
                    x1, y1, x2, y2 = map(int, box)
                    label = f"Person {confidence * 100:.1f}%"
                    cv2.rectangle(frame_bgr, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(frame_bgr, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            cv2.imshow("YOLOv8 Person Detection", frame_bgr)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop()
                self.capture_thread.stop()
                break
                
    def stop(self):
        self.stopped = True

def main():
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(
        main={"size": (360, 360)},
        transform=libcamera.Transform(hflip=True, vflip=True)))
    picam2.start()

    model = YOLO("yolov8n.pt")

    capture_thread = CaptureThread(picam2)
    inference_thread = InferenceThread(capture_thread, model, fps=3)    # FPS LIMIT

    capture_thread.start()
    inference_thread.start()

    inference_thread.join()
    capture_thread.join()

    picam2.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
