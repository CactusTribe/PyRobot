import RPi.GPIO as GPIO
import sys, time

class FrontLight:

	def __init__(self, pin):
		self.no_pin = pin
		self.poweron = False

		GPIO.setup(self.no_pin, GPIO.OUT)

	def on(self):
		self.poweron = True
		GPIO.output(self.no_pin, True)

	def off(self):
		self.poweron = False
		GPIO.output(self.no_pin, False)

	def flash(self, timer):
		self.on()
		time.sleep(int(timer))
		self.off()

	def isOn(self):
		return self.poweron


if __name__ == "__main__":

	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)

	if len(sys.argv) > 2:
		FrontLight = FrontLight(int(sys.argv[1]))

		FrontLight.on()
		time.sleep(int(sys.argv[2]))
		FrontLight.off()

	elif len(sys.argv) == 2:
		FrontLight = FrontLight(int(sys.argv[1]))

		FrontLight.on()
		time.sleep(1)
		FrontLight.off()
	else:
		print("Usage: FrontLight <pin> <timer(*option)(sec.)>")
