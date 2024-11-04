import RPi.GPIO as GPIO
import tkinter as tk
from tkinter import ttk
import threading

BUTTON_PIN = 15
LED_PIN = 4

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)

class PushButtonApp:
    def __init__(self, master):
        self.master = master
        master.title("PUSH button monitor")
        master.geometry("300x190")
        
        self.label = ttk.Label(master, text="button : ready", anchor='center', justify='center')
        self.label.pack(pady=20)
        
        self.count_label = ttk.Label(master, text="button pushed: 0")
        self.count_label.pack(pady=10)
        
        self.quit_button = ttk.Button(master, text="quit", command=self.quit)
        self.quit_button.pack(pady=10)
        
        self.button_count = 0
        self.is_running = True
        self.button_pressed = False
                
        self.monitor_thread = threading.Thread(target=self.monitor_gpio)
        self.monitor_thread.start()
        
    def monitor_gpio(self):
        while self.is_running:
            if GPIO.input(BUTTON_PIN) == GPIO.HIGH:
                if not self.button_pressed:
                    self.button_count += 1
                    self.update_gui(pressed=True)
                    self.button_pressed = True
                GPIO.output(LED_PIN, GPIO.HIGH)
            else:
                if self.button_pressed:
                    self.update_gui(pressed=False)
                GPIO.output(LED_PIN, GPIO.LOW)
                self.button_pressed = False
                
            self.master.update()
        
    def update_gui(self, pressed):
        if pressed:
            self.label.config(text="button status : pushed\n\n딸-깍")
        else:
            self.label.config(text="button status : ready")
        self.count_label.config(text=f"button pushed: {self.button_count}")
            
    def quit(self):
        self.is_running = False
        GPIO.cleanup()
        self.master.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = PushButtonApp(root)
    root.protocol("WM_DELETE_WINDOW", app.quit)
    root.mainloop()