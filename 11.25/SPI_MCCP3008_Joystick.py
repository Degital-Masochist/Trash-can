import spidev
import time

delay = 0.5

sw_channel = 0
vrx_channel = 1
vry_channel = 2

spi = spidev.SpiDev()

spi.open(0, 0)

spi.max_speed_hz = 100000

def readadc(adcnum):
	if adcnum > 7 or adcnum < 0:
		return -1
	r = spi.xfer2([1, 8 + adcnum << 4, 0])
	data = ((r[1] & 3) << 8) + r[2]
	return data
	
while True:
	vrx_pos = readadc(vrx_channel)
	vry_pos = readadc(vry_channel)
	
	sw_val = readadc(sw_channel)
	
	print("X : {} Y : {} SW : {}".format(vrx_pos, vry_pos, sw_val))
	
	time.sleep(delay)
