import serial
import pynmea2

class GPSReader:
	def __init__(self, port="/dev/ttyS0", baudrate = 9600, timeout = 1):
		self.serial_port = serial.Serial(port, baudrate = baudrate, timeout = timeout)
		
	def get_speed(self):
		try:
			while True:
				data = self.serial_port.readline().decode('utf-8', errors='ignore')
				if data.startswith('$GPRMC'):
					msg = pynmea2.parse(data)
					if msg.status == 'A':
						speed_knots = float(msg.spd_over_grnd)
						speed_kmh = speed_knots * 1.852
						return speed_kmh
						
		except Exception as e:
			print(f"GPS ERROR : {e}")
			return 0 
