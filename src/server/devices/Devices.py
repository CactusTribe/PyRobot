from devices.FrontLight import FrontLight
from devices.MCP3008_SPI import MCP3008
from devices.LED_RGB import LED_RGB
from devices.Motor_DC import Motor_DC
from devices.MQ_XX import *
from devices.HC_SR04 import HC_SR04
from picamera import PiCamera

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)	

camera = PiCamera()
camera.resolution = (480,320)
#camera.framerate = 20

# Devices (Capteurs , éclairage, etc)
FrontLight_W = FrontLight(18)        		# PIN : WHITE
FrontLight_IR = FrontLight(23)					# PIN : IR
StatusLED = LED_RGB(17, 27, 22)				  # PIN : R, G, B

HC_SR04_R = HC_SR04(19, 26) 						# PIN : TRIGGER, ECHO
HC_SR04_L = HC_SR04(6, 13) 							# PIN : TRIGGER, ECHO
DHT22 = 5																# PIN : AOUT

Motor_L = Motor_DC(21, 20, 16) 					# PIN : SPEED, FW, BW
Motor_R = Motor_DC(12, 25, 24)			  	# PIN : SPEED, FW, BW

MCP3008_1 = MCP3008(0)									# SPI device number
MCP3008_2 = MCP3008(1)									# SPI device number

MQ_2 = MQ_2(MCP3008_2, 0, 9.83)  				# MCP, CHANNEL, CLEAN_AIR_FACTOR
MQ_3 = MQ_3(MCP3008_2, 1, 60)  					# MCP, CHANNEL, CLEAN_AIR_FACTOR
MQ_4 = MQ_4(MCP3008_2, 2, 1)  					# MCP, CHANNEL, CLEAN_AIR_FACTOR
MQ_5 = MQ_5(MCP3008_2, 3, 6.5)  				# MCP, CHANNEL, CLEAN_AIR_FACTOR
MQ_6 = MQ_6(MCP3008_2, 4, 10)  	  			# MCP, CHANNEL, CLEAN_AIR_FACTOR
MQ_7 = MQ_7(MCP3008_2, 5, 28)  	  			# MCP, CHANNEL, CLEAN_AIR_FACTOR
MQ_8 = MQ_8(MCP3008_2, 6, 1)  	  			# MCP, CHANNEL, CLEAN_AIR_FACTOR
MQ_135 = MQ_135(MCP3008_2, 7, 3.6) 			# MCP, CHANNEL, CLEAN_AIR_FACTOR