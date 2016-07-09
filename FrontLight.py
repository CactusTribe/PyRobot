import RPi.GPIO as GPIO
import sys, time

class FrontLight:

	def __init__(self, pin, luminosity):
		self.no_pin = pin
		self.luminosity = luminosity

		GPIO.setup(self.no_pin, GPIO.OUT)
		# creation d'un objet PWM. canal=4 frequence=50Hz
		self.Light = GPIO.PWM(self.no_pin, 50)
		# demarrage du PWM avec un cycle a 0 (LED off)
		self.Light.start(self.luminosity)

	def setLuminosity(self, lum):
		self.luminosity = lum 
		self.Light.ChangeDutyCycle(self.luminosity)

	def on(self):
		self.Light.ChangeDutyCycle(100)

	def off(self):
		self.Light.ChangeDutyCycle(0)


if __name__ == "__main__":

	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)

	if len(sys.argv) > 3:
		FrontLight = FrontLight(int(sys.argv[1]), int(sys.argv[2]))
		time.sleep(int(sys.argv[3]))

	elif len(sys.argv) == 3:
		FrontLight = FrontLight(int(sys.argv[1]), int(sys.argv[2]))
		time.sleep(1)
	else:
		print("Usage: FrontLight <pin> <luminosity(%)> <timer(*option)(sec.)>")

	GPIO.cleanup()