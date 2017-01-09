from ThreadClient import ThreadClient
from devices.Devices import *

class MainModule(ThreadClient):
	def __init__(self, name):
		ThreadClient.__init__(self, name)

	# Execute command
	def execute_cmd(self, cmd):
		args = cmd.split(" ")
		cmd = args[0]

		if cmd == "sled":
			self.StatusLED_commands(args)

		elif cmd == "fl":
			self.FrontLight_commands(args)

	# --------------------------------------------
	# MODULE STATUS-LED
	# --------------------------------------------
	def StatusLED_commands(self, args):
		try:

			if args[1] == "red":
				StatusLED.setColor_RGB(255, 0, 0)
				StatusLED.blink(0.5)

			elif args[1] == "green":
				StatusLED.setColor_RGB(0, 255, 0)
				StatusLED.blink(0.5)

			elif args[1] == "blue":
				StatusLED.setColor_RGB(0, 0, 255)
				StatusLED.blink(0.5)
				
			elif args[1] == "rgb":
				StatusLED.setColor_RGB(int(args[2]), int(args[3]), int(args[4]))
				StatusLED.blink(0.5)

		except: pass

	# --------------------------------------------
	# MODULE FRONT-LIGHTS
	# --------------------------------------------
	def FrontLight_commands(self, args):
		try:
			if args[1] == "w":
				if args[2] == "on":
					FrontLight_W.on()

				elif args[2] == "off":
					FrontLight_W.off()

				elif args[2] == "flash":
					t = threading.Thread(target = FrontLight_W.flash, args = [args[2]] )
					t.start()
					
				elif args[2] == "status":
					self.tcp_send("fl status {}".format(FrontLight_W.isOn()))				

			elif args[1] == "ir":

				if args[2] == "on":
					FrontLight_IR.on()

				elif args[2] == "off":
					FrontLight_IR.off()

				elif args[2] == "flash":
					t = threading.Thread(target = FrontLight_IR.flash, args = [args[2]] )
					t.start()
					
				elif args[2] == "status":
					self.tcp_send("fl status {}".format(FrontLight_IR.isOn()))	

			elif args[1] == "lum":
				FrontLight_W.setLuminosity(int(args[2]))
				FrontLight_IR.setLuminosity(int(args[2]))

				if FrontLight_W.poweron == True:
					FrontLight_W.on()
				if FrontLight_IR.poweron == True:
					FrontLight_IR.on()

		except: pass