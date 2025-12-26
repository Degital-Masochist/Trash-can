import network 
import urequests
import uasyncio as asyncio
import time
from machine import Pin, time_pulse_us

MCU_ID = "1"
#HOT sopt Network set
SSID = "IGONAN"
PASSWORD = "12345667"
SERVER_IP = "10.53.184.208"

#ipTIME local Network set
#SSID = "1557"
#PASSWORD = "12345667"
#SERVER_IP = "10.0.0.1"

pin_r = Pin(15, Pin.OUT)
pin_g = Pin(2, Pin.OUT)
pin_b = Pin(4, Pin.OUT)
TRIG = Pin(0, Pin.OUT)
ECHO = Pin(1, Pin.IN)

wlan = network.WLAN(network.STA_IF)

led_color = "off"

def now_hms():
    t = time.localtime()
    return "{:02d}:{:02d}:{:02d}".format(t[3], t[4], t[5])

def connect_wifi():
    if wlan.isconnected():
        ssid = wlan.config('essid')
        ip = wlan.ifconfig()[0]
        print("Already Connected\n", ssid, "|", ip)
        return True
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    for _ in range(10):
        if wlan.isconnected():
            ssid = wlan.config('essid')
            ip = wlan.ifconfig()[0]
            print("Connected\n", ssid, "|", ip)
            return True
        time.sleep(1)
    return False

def set_led_color(c):
    if c == "red":
        pin_r.value(0); pin_g.value(1); pin_b.value(1)
    elif c == "yellow":
        pin_r.value(0); pin_g.value(0); pin_b.value(1)
    elif c == "green":
        pin_r.value(1); pin_g.value(1); pin_b.value(1)
    elif c == "blue":
        pin_r.value(1); pin_g.value(1); pin_b.value(0)
    elif c == "off":
        pin_r.value(1); pin_g.value(1); pin_b.value(1)
    else:
        pin_r.value(1); pin_g.value(1); pin_b.value(1)

def get_distance():
    TRIG.low()
    time.sleep_us(2)
    TRIG.high()
    time.sleep_us(10)
    TRIG.low()
    d = time_pulse_us(ECHO, 1, 30000)
    return (d / 2) / 29.1

def send_signal(s=0):
    if not wlan.isconnected():
        return
    try:
        r = urequests.post(
            "http://{}:1557/update".format(SERVER_IP),
            json={"id": MCU_ID, "signal": s},
            timeout=1
        )
        r.close()
    except:
        pass

def fetch_led_status():
    if not wlan.isconnected():
        return "yellow"
    try:
        r = urequests.get(
            "http://{}:1557/api/led_status/{}".format(SERVER_IP, MCU_ID),
            timeout=1
        )
        if r.status_code == 200:
            c = r.json().get("color", "off")
            r.close()
            return c
        r.close()
    except:
        pass
    return "yellow"

async def task_led_status():
    global led_color
    while True:
        if wlan.isconnected():
            led_color = fetch_led_status()
        await asyncio.sleep(2)

async def task_led_apply():
    prev_color = None
    while True:
        if led_color != prev_color:
            set_led_color(led_color)
            print(now_hms(), led_color)
            prev_color = led_color
        await asyncio.sleep(2)

async def task_distance():
    while True:
        if not wlan.isconnected():
            ok = connect_wifi()
            if not ok:
                await asyncio.sleep(5)
                continue
        d = get_distance()
        if d >= 0:
            print(now_hms(), d, "cm")
            if d < 60:
                if led_color == "blue":
                    send_signal(4)
                else:
                    send_signal(1)
            else:
                send_signal(0)
        else:
            print(now_hms(), "sensor error")
            send_signal(3)
        await asyncio.sleep(1)

async def main():
    connect_wifi()
    asyncio.create_task(task_led_status())
    asyncio.create_task(task_led_apply())
    asyncio.create_task(task_distance())
    while True:
        await asyncio.sleep(1)

asyncio.run(main())

