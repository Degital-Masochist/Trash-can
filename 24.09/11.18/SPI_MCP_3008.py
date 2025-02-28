import spidev
import time

delay = 0.5
pot_channel = 0

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

def readadc(adcnum):
	if adcnum > 7 or adcnum < 0:
		return -1
		
	r = spi.xfer2([1, 8 + adcnum << 4, 0])
	print(f"Raw SPI data: {r}")
	data = ((r[1] & 3) << 8) + r[2]
	return data
	
try:
	while True:
		pot_value = readadc(pot_channel)
		voltage = pot_value * (3.3 / 1023.0)
		print("-----------------------")
		print(f"ADC Value: {pot_value}")
		print(f"Voltage : {voltage:.2f}V")
		time.sleep(delay)
		
except KeyboardInterrupt:
	print("\nProgram terminated by user")
finally:
	spi.close()
	print("SPI connection closed")
