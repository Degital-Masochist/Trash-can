import serial

def main():
    # Set up the serial port and baud rate
    port = '/dev/serial0'  # Replace with your serial port if different
    baud_rate = 9600       # Adjust based on your GPS module's baud rate

    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        print(f"Connected to port: {port}, baud rate: {baud_rate}")
    except serial.SerialException as e:
        print(f"Error connecting to serial port: {e}")
        return

    try:
        while True:
            # Read a line from the serial port, decode, and strip whitespace
            line = ser.readline().decode('ascii', errors='replace').strip()
            if line:
                print(line)
    except KeyboardInterrupt:
        print("Program terminated by user.")
    finally:
        ser.close()

if __name__ == '__main__':
    main()
