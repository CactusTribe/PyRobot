import RPi.GPIO as GPIO
import sys, time

class Sensor:

	def __init__(self, pin):
		self.no_pin = pin

		GPIO.setup(self.no_pin, GPIO.OUT)
		# creation d'un objet PWM. canal=4 frequence=50Hz
		self.Sens = GPIO.PWM(self.no_pin, 50)
		# demarrage du PWM avec un cycle a 0 (LED off)
		self.Sens.start(self.luminosity)

	def getValue(self):
		return 0

	def capture(self):
		print("Reading values ...")


if __name__ == "__main__":

	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)

	if len(sys.argv) == 2:
		Sensor = Sensor(int(sys.argv[1]))
	else:
		print("Usage: Sensor <pin>")

	GPIO.cleanup()