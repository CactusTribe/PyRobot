from ThreadClient import ThreadClient
from devices.Devices import *
import SharedParams

from enum import Enum
class Direction(Enum):
	FORWARD = 1
	BACKWARD = 2
	LEFT = 3
	RIGHT = 4

class IAModule(ThreadClient):
	def __init__(self, name):
		ThreadClient.__init__(self, name)
		self.stopped = True

	# Execute command
	def execute_cmd(self, cmd):
		args = cmd.split(" ")
		cmd = args[0]

		if cmd == "ia":
			self.IA_commands(args)

	# --------------------------------------------
	# IA ENGINE
	# --------------------------------------------
	def IA_commands(self, args):
		try:
			if args[1] == "auto":
				self.stopped = False
				print("AutoMode started")
				th = threading.Thread(target = self.auto_mode, args = [] )
				th.start()

			elif args[1] == "stop":
				print("IA stoped")
				self.stopped = True
	
		except Exception as e:
			print(e) 


	def auto_mode(self):
		print("AutoMode started")
		last_dist_IR = 0

		dist_min = 5
		dist_max = 8

		direction = Direction.FORWARD

		while self.stopped == False:
			try:
				dist_IR = MCP3008_1.getValue(4)
				dist_IR = (2076 / (dist_IR - 11)) if (dist_IR > 12) else 100

				if dist_IR < dist_max and dist_IR >= dist_min:
					Motor_L.setDirection("fw")
					Motor_R.setDirection("fw")
					Motor_L.setSpeed(SharedParams.engine_speed)
					Motor_R.setSpeed(SharedParams.engine_speed)
					direction = Direction.FORWARD

				else:
					StatusLED.setColor_RGB(100, 0, 255)
					StatusLED.blink(0.1)

					Motor_L.setSpeed(0)
					Motor_R.setSpeed(0)
					Motor_L.setDirection("bw")
					Motor_R.setDirection("bw")
					Motor_L.setSpeed(SharedParams.engine_speed)
					Motor_R.setSpeed(SharedParams.engine_speed)
					direction = Direction.BACKWARD
					time.sleep(0.5)

					Motor_L.setSpeed(0)
					Motor_R.setSpeed(0)
					Motor_L.setDirection("fw")
					Motor_R.setDirection("bw")
					Motor_L.setSpeed(SharedParams.engine_speed)
					Motor_R.setSpeed(SharedParams.engine_speed)
					direction = Direction.RIGHT
					time.sleep(1)
						
								
				last_dist_IR = dist_IR	
				time.sleep(0.02)
				
			except Exception as e:
				Motor_L.setSpeed(0)
				Motor_R.setSpeed(0)
				print(e)

		Motor_L.setSpeed(0)
		Motor_R.setSpeed(0)