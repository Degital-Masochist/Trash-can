import network
import urequests
import time
from machine import Pin, time_pulse_us

MCU_ID = "1"
SSID = 'IGONAN'
PASSWORD = '12345667'
SERVER_IP = '192.168.6.240'
#SSID = '1557'
#PASSWORD = '12345678'
#SERVER_IP = '10.5.9.7'

pin_r = Pin(15, Pin.OUT)
pin_g = Pin(2, Pin.OUT)
pin_b = Pin(4, Pin.OUT)
TRIG = Pin(0, Pin.OUT)
ECHO = Pin(1, Pin.IN)

wlan = network.WLAN(network.STA_IF)

def connect_wifi():
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(SSID, PASSWORD)
        for _ in range(15):
            if wlan.isconnected():
                print("CONNECT SUCCESS")
                return True
            print("RECONNECT")
            time.sleep(1)
        return False
    return True

def set_led_color(color):
    if color == 'red':
        pin_r.value(0); pin_g.value(1); pin_b.value(1)
        print("RED")
    elif color == 'yellow':
        pin_r.value(0); pin_g.value(0); pin_b.value(1)
        print("YELLOW")
    elif color == 'green':
        pin_r.value(1); pin_g.value(1); pin_b.value(1)
        print("OFF(GREEN)")
    else:
        pin_r.value(1); pin_g.value(1); pin_b.value(1)
        print("OFF(ELSE)")

def get_led_status_from_server():
    try:
        res = urequests.get(f'http://{SERVER_IP}:1557/api/led_status/{MCU_ID}')
        if res.status_code == 200:
            color = res.json().get('color', 'off')
            res.close()
            return color
        res.close()
    except:
        pass
    return 'yellow'

def send_signal(signal=0):
    data = {"id": MCU_ID, "signal": signal}
    try:
        res = urequests.post(f'http://{SERVER_IP}:1557/', json=data)
        res.close()
    except:
        pass

def get_distance():
    TRIG.low()
    time.sleep_us(2)
    TRIG.high()
    time.sleep_us(10)
    TRIG.low()
    duration = time_pulse_us(ECHO, 1, 30000)
    distance = (duration / 2) / 29.1
    return distance

connect_wifi()

while True:
    if not wlan.isconnected():
        connect_wifi()
    distance = get_distance()
    print("Distance:", distance, "cm")
    if distance < 60:
        send_signal(1)
    else:
        send_signal(0)
    color = get_led_status_from_server()
    set_led_color(color)
    time.sleep(5)
