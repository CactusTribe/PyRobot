from ThreadClient import ThreadClient
from devices.Devices import *

class SensorsModule(ThreadClient):
	def __init__(self, name):
		ThreadClient.__init__(self, name)

	# Execute command
	def execute_cmd(self, cmd):
		args = cmd.split(" ")
		cmd = args[0]

		if cmd == "sns":
			self.Sensors_commands(args)

	# --------------------------------------------
	# MODULE SENSORS
	# --------------------------------------------
	def Sensors_commands(self, args):
		global humidity, temperature

		try:

			if len(args) > 1:
				start = time.time()
				elapsed = 0
				timer = 12

				while True:
					value = MCP3008_1.getValue(int(args[1]))
					self.tcp_send("sns "+args[1]+" "+str(value))
					time.sleep(0.5) 

					elapsed = time.time() - start
					if elapsed >= timer:
						break

			else:
				values = [] 
				for e in range(8):
					values += [MCP3008_1.getValue(e)]

				luminosity_R = values[0]
				luminosity_L = values[1]
				sound 			 = int(values[2]*1.5)
				inclinaison  = values[3]
				dist_IR	     = values[4]
				channel_5 	 = values[5]
				channel_6 	 = values[6]
				channel_7 	 = values[7]

				gas_1 			 = int(MQ_135.MQGetGasPercentage("GAS_CH3_2CO"))
				gas_2 			 = int(MQ_2.MQGetGasPercentage("GAS_SMOKE"))
				gas_3 			 = str(MQ_3.MQGetGasPercentage("GAS_ALCOHOL"))[:5]
				gas_4 			 = int(MQ_4.MQGetGasPercentage("GAS_CH4"))
				gas_5 			 = int(MQ_5.MQGetGasPercentage("GAS_CH4"))
				gas_6 			 = int(MQ_6.MQGetGasPercentage("GAS_LPG"))
				gas_7 			 = int(MQ_7.MQGetGasPercentage("GAS_CO"))
				gas_8 			 = int(MQ_8.MQGetGasPercentage("GAS_H2"))

				dist_L 	 = int(distance_L)
				dist_R 	 = int(distance_R)

				self.tcp_send("sns {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {}".format(
					luminosity_L, luminosity_R, sound, inclinaison, dist_IR, channel_5, channel_6, channel_7, 
					gas_1, gas_2, gas_3, gas_4, gas_5, gas_6, gas_7, gas_8,
					dist_L, dist_R, temperature, humidity ))
					
		except Exception as e:
			print(e)
			self.tcp_send("sns 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0")
