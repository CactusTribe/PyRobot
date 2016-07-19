import RPi.GPIO as GPIO
import sys, time

class FrontLight:

	def __init__(self, pin):
		self.no_pin = pin
		self.luminosity = 0
		self.poweron = False

		GPIO.setup(self.no_pin, GPIO.OUT)
		# creation d'un objet PWM. canal=4 frequence=50Hz
		self.Light = GPIO.PWM(self.no_pin, 50)
		# demarrage du PWM avec un cycle a 0 (LED off)
		self.Light.start(self.luminosity)

	def setLuminosity(self, lum):
		self.luminosity = lum 
		self.Light.ChangeDutyCycle(self.luminosity)

	def on(self):
		self.poweron = True
		self.luminosity = 100 
		self.Light.ChangeDutyCycle(self.luminosity)

	def off(self):
		self.poweron = False
		self.luminosity = 0
		self.Light.ChangeDutyCycle(self.luminosity)

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
