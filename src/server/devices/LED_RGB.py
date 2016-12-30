import RPi.GPIO as GPIO
import time, sys

class LED_RGB:

	def __init__(self, pin_R, pin_G, pin_B):
		self.no_pin_R = pin_R
		self.no_pin_G = pin_G
		self.no_pin_B = pin_B

		GPIO.setup(self.no_pin_R, GPIO.OUT)
		GPIO.setup(self.no_pin_G, GPIO.OUT)
		GPIO.setup(self.no_pin_B, GPIO.OUT)

		# creation d'un objet PWM. canal=4 frequence=50Hz
		self.LEDR = GPIO.PWM(self.no_pin_R, 50)
		self.LEDG = GPIO.PWM(self.no_pin_G, 50)
		self.LEDB = GPIO.PWM(self.no_pin_B, 50)

		self.sat_R = 255
		self.sat_G = 255
		self.sat_B = 255

		# demarrage du PWM avec un cycle a 0 (LED off)
		self.LEDR.start(0)
		self.LEDG.start(0)
		self.LEDB.start(0)

	def __str__(self):
		return ("[GPIO] r{} g{} b{} [Color] r{} g{} b{}".format(self.no_pin_R, self.no_pin_G, self.no_pin_B, self.sat_R, self.sat_G, self.sat_B))

	def on(self):
		self.LEDR.ChangeDutyCycle((self.sat_R/255)*100)
		self.LEDG.ChangeDutyCycle((self.sat_G/255)*100)
		self.LEDB.ChangeDutyCycle((self.sat_B/255)*100)

	def off(self):
		self.LEDR.ChangeDutyCycle(0)
		self.LEDG.ChangeDutyCycle(0)
		self.LEDB.ChangeDutyCycle(0)

	def setColor_RGB(self, r, g, b):
		self.sat_R = r
		self.sat_G = g
		self.sat_B = b

	def blink(self, timer):
		for dc in range(0, 101, 1):
			self.LEDR.ChangeDutyCycle((self.sat_R/255)*dc)
			self.LEDG.ChangeDutyCycle((self.sat_G/255)*dc)
			self.LEDB.ChangeDutyCycle((self.sat_B/255)*dc)
			time.sleep(timer/200)
		for dc in range(100, -1, -1):
			self.LEDR.ChangeDutyCycle((self.sat_R/255)*dc)
			self.LEDG.ChangeDutyCycle((self.sat_G/255)*dc)
			self.LEDB.ChangeDutyCycle((self.sat_B/255)*dc)
			time.sleep(timer/200)


if __name__ == "__main__":
	if len(sys.argv) > 3:

		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)

		led = LED_RGB(17, 27, 22)
		led.setColor_RGB(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
		led.blink(0.5)

		GPIO.cleanup()