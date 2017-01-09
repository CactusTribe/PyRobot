from ThreadClient import ThreadClient
from devices.Devices import *

class EngineModule(ThreadClient):
	def __init__(self, name):
		ThreadClient.__init__(self, name)

	# Execute command
	def execute_cmd(self, cmd):
		args = cmd.split(" ")
		cmd = args[0]

		if cmd == "eng":
			self.Engine_commands(args)

	# --------------------------------------------
	# MODULE ENGINE
	# --------------------------------------------
	def Engine_commands(self, args):
		global engine_speed

		try:
			if args[1] == "fw":
				timer = float(args[2])

				Motor_L.setDirection("fw")
				Motor_R.setDirection("fw")

				Motor_L.setSpeed(engine_speed)
				Motor_R.setSpeed(engine_speed)

				t1 = time.time()

				while (time.time() - t1) <= timer:

					if (int(MCP3008_1.getValue(2)*100/1024)) > 55:
						StatusLED.setColor_RGB(100, 0, 255)
						StatusLED.blink(0.1)
						break

					time.sleep(0.02)

				Motor_L.setSpeed(0)
				Motor_R.setSpeed(0)

			elif args[1] == "bw":
				timer = float(args[2])

				Motor_L.setDirection("bw")
				Motor_R.setDirection("bw")

				Motor_L.setSpeed(engine_speed)
				Motor_R.setSpeed(engine_speed)
				time.sleep(timer)
				Motor_L.setSpeed(0)
				Motor_R.setSpeed(0)

			elif args[1] == "l":
				timer = float(args[2])

				Motor_L.setDirection("bw")
				Motor_R.setDirection("fw")

				Motor_L.setSpeed(engine_speed)
				Motor_R.setSpeed(engine_speed)
				time.sleep(timer)
				Motor_L.setSpeed(0)
				Motor_R.setSpeed(0)

			elif args[1] == "r":
				timer = float(args[2])

				Motor_L.setDirection("fw")
				Motor_R.setDirection("bw")

				Motor_L.setSpeed(engine_speed)
				Motor_R.setSpeed(engine_speed)
				time.sleep(timer)
				Motor_L.setSpeed(0)
				Motor_R.setSpeed(0)

			elif args[1] == "forward": 

				if MCP3008_1.getValue(4) >= 15:
					dist_IR = (2076 / (MCP3008_1.getValue(4) - 11) )
				else:
					dist_IR = 100

				inclinaison = (MCP3008_1.getValue(3)*100)/1024

				if (inclinaison < 50) or (inclinaison > 50 and dist_IR < 10):
					Motor_L.setDirection("fw")
					Motor_R.setDirection("fw")
					Motor_L.setSpeed(engine_speed)
					Motor_R.setSpeed(engine_speed)

			elif args[1] == "backward":
				Motor_L.setDirection("bw")
				Motor_R.setDirection("bw")
				Motor_L.setSpeed(engine_speed)
				Motor_R.setSpeed(engine_speed)

			elif args[1] == "left":
				Motor_L.setDirection("bw")
				Motor_R.setDirection("fw")
				Motor_L.setSpeed(engine_speed)
				Motor_R.setSpeed(engine_speed)

			elif args[1] == "right":
				Motor_L.setDirection("fw")
				Motor_R.setDirection("bw")
				Motor_L.setSpeed(engine_speed)
				Motor_R.setSpeed(engine_speed)

			elif args[1] == "stop":
				Motor_L.setSpeed(0)
				Motor_R.setSpeed(0)

			elif args[1] == "speed":
				engine_speed = int(args[2])

		except Exception as e:
			print(e) 