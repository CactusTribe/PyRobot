import time, sys
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO_TRIGGER = 19
GPIO_ECHO = 26

NB_LOOP = 8

print("Ultrasonic Measurement :")

GPIO.setup(GPIO_TRIGGER,GPIO.OUT)  # Trigger
GPIO.setup(GPIO_ECHO,GPIO.IN)      # Echo

# Set trigger to False (Low)
GPIO.output(GPIO_TRIGGER, False)

# Allow module to settle
time.sleep(0.5)

while True:

	echantillons = []

	for i in range(NB_LOOP):
		# Send 10us pulse to trigger
		GPIO.output(GPIO_TRIGGER, True)
		time.sleep(0.00001)
		GPIO.output(GPIO_TRIGGER, False)
		start = time.time()

		while GPIO.input(GPIO_ECHO)==0:
		  start = time.time()

		while GPIO.input(GPIO_ECHO)==1:
		  stop = time.time()

		# Calculate pulse length
		elapsed = stop-start

		# Distance pulse travelled in that time is time
		# multiplied by the speed of sound (cm/s)
		distance = elapsed * 34000

		# That was the distance there and back so halve the value
		distance = distance / 2
		echantillons += [distance]

	echantillons.remove(max(echantillons))
	echantillons.remove(min(echantillons))

	average = sum(echantillons) / len(echantillons)

	sys.stdout.write("\rDistance : {} cm       ".format(int(average)))
	sys.stdout.flush()
	time.sleep(0.2)

# Reset GPIO settings
GPIO.cleanup()