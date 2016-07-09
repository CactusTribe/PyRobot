import time, sys
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

# Hardware SPI config:
SPI_PORT = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

print("Reading MCP3008 values, press Ctrl-C to quit...")

print("| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |".format(*range(8)))
print("-" * 57)

while True:
	# Read values
	values = [0]*8
	for i in range(8):
		values[i] = mcp.read_adc(i)

	# Print values
	sys.stdout.write("\r| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |".format(*values))
	sys.stdout.flush()
	time.sleep(0.5)