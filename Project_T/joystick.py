from evdev import InputDevice, ecodes, list_devices
import threading

def find_gamepad(keywords=None):
    if keywords is None:
        keywords = ["8BitDo", "joystick", "gamepad"]
    keywords = [k.lower() for k in keywords]

    devices = [InputDevice(path) for path in list_devices()]
    for joystick in devices:
        name_lower = joystick.name.lower()
        if any(keyword in name_lower for keyword in keywords):
            print(f"Matched device: {joystick.name} at {joystick.path}")
            print("/////Joystick CONNECTED/////")
            return InputDevice(joystick.path)
    print("No matching gamepad found.")
    return None

gamepad = find_gamepad()

if gamepad is None:
    print("Gamepad not found")
    exit(1)
