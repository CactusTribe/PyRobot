import RPi.GPIO as GPIO
import sys, time

class Motor_DC:

	def __init__(self, pin_speed, pin_fw, pin_bw):
		self.no_pin_speed = pin_speed
		self.no_pin_fw = pin_fw
		self.no_pin_bw = pin_bw
		self.speed = 0

		GPIO.setup(self.no_pin_speed, GPIO.OUT)
		GPIO.setup(self.no_pin_fw, GPIO.OUT)
		GPIO.setup(self.no_pin_bw, GPIO.OUT)

		self.MotorSpeed = GPIO.PWM(self.no_pin_speed, 50)
		self.MotorSpeed.start(self.speed)
		self.setDirection("fw")

	def setSpeed(self, speed):
		self.speed = speed 
		self.MotorSpeed.ChangeDutyCycle(self.speed)

	def setDirection(self, direction):
		if direction == "fw":
			GPIO.output(self.no_pin_fw, True)
			GPIO.output(self.no_pin_bw, False)
		elif direction == "bw":
			GPIO.output(self.no_pin_fw, False)
			GPIO.output(self.no_pin_bw, True)


if __name__ == "__main__":

	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)

	Motor_L = Motor_DC(13, 19, 26)
	Motor_R = Motor_DC(23, 24, 25)

	Motor_L.setSpeed(100)
	Motor_R.setSpeed(100)
	time.sleep(5)
	Motor_L.setSpeed(0)
	Motor_R.setSpeed(0)
	time.sleep(1)

	Motor_L.setDirection("bw")
	Motor_R.setDirection("bw")

	Motor_L.setSpeed(100)
	Motor_R.setSpeed(100)
	time.sleep(5)

	Motor_L.setSpeed(0)
	Motor_R.setSpeed(0)
