import time, sys
import RPi.GPIO as GPIO

class HC_SR04:
	def __init__(self, trig_pin, echo_pin):
		self.trigger = trig_pin
		self.echo = echo_pin

		GPIO.setup(self.trigger, GPIO.OUT)  # Trigger
		GPIO.setup(self.echo, GPIO.IN)      # Echo

		# Set trigger to False (Low)
		GPIO.output(self.trigger, False)

	def getDistance(self):
		# Send 10us pulse to trigger
		GPIO.output(self.trigger, True)
		time.sleep(0.00001)
		GPIO.output(self.trigger, False)
		start = time.time()

		while GPIO.input(self.echo)==0:
		  start = time.time()

		while GPIO.input(self.echo)==1:
		  stop = time.time()

		# Calculate pulse length
		elapsed = stop-start
		# Distance pulse travelled in that time is time
		# multiplied by the speed of sound (cm/s)
		distance = elapsed * 34000
		# That was the distance there and back so halve the value
		distance = distance / 2

		return distance

	def capture(self):
		
		while True:
			NB_LOOP = 8
			echantillons = []

			for i in range(NB_LOOP):
				distance = self.getDistance()
				echantillons += [distance]

			echantillons.remove(max(echantillons))
			echantillons.remove(min(echantillons))

			average = sum(echantillons) / len(echantillons)

			sys.stdout.write("\rDistance : {} cm       ".format(int(average)))
			sys.stdout.flush()
			time.sleep(0.2)

if __name__ == "__main__":

	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)

	HC_SR04 = HC_SR04(19, 26)
	HC_SR04.capture()

	GPIO.cleanup()