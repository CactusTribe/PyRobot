import socket, sys, subprocess, time, threading, math
import RPi.GPIO as GPIO

from MCP3008_SPI import MCP3008

class MQ_XX:
	def __init__(self, mcp3008, channel, resistance, clean_air_factor):

		#### HARDWARE ####
		self.MCP3008 = mcp3008
		self.MQ_CHANNEL = channel
		self.RL_VALUE = resistance #(komhs)
		self.RO_CLEAN_AIR_FACTOR = clean_air_factor # RO_CLEAR_AIR_FACTOR = (Sensor resistance in clean air) / RO ,
																								# which is derived from the chart in datasheet
		self.RO = 10
		
		#### SOFTWARE ###
		self.CALIBARAION_SAMPLE_TIMES = 10			# define how many samples you are going to take in the calibration phase
		self.CALIBRATION_SAMPLE_INTERVAL = 100	# define the time interal(in milisecond) between each samples in the
																						# cablibration phase
		self.READ_SAMPLE_TIMES = 1							# define how many samples you are going to take in normal operation
		self.READ_SAMPLE_INTERVAL = 0 					# define the time interal(in milisecond) between each samples in 
																						# normal operation    

	def MQCalibration(self):
		"""***************************** MQCalibration ****************************************
		Input:   mq_pin - analog channel
		Output:  Ro of the sensor
		Remarks: This function assumes that the sensor is in clean air. It use  
		         MQResistanceCalculation to calculates the sensor resistance in clean air 
		         and then divides it with RO_CLEAN_AIR_FACTOR. RO_CLEAN_AIR_FACTOR is about 
		         10, which differs slightly between different sensors.
		************************************************************************************"""
		val = 0.0

		for e in range(self.CALIBARAION_SAMPLE_TIMES):
			val += self.MQResistanceCalculation()
			time.sleep(self.CALIBRATION_SAMPLE_INTERVAL/1000)

		val = val / self.CALIBARAION_SAMPLE_TIMES
		val = val / self.RO_CLEAN_AIR_FACTOR

		self.RO = val

	def MQRead(self):
		"""*****************************  MQRead *********************************************
		Input:   mq_pin - analog channel
		Output:  Rs of the sensor
		Remarks: This function use MQResistanceCalculation to caculate the sensor resistenc (Rs).
		         The Rs changes as the sensor is in the different consentration of the target
		         gas. The sample times and the time interval between samples could be configured
		         by changing the definition of the macros.
		************************************************************************************"""
		rs = 0

		for e in range(self.READ_SAMPLE_TIMES):
			rs += self.MQResistanceCalculation()
			time.sleep(self.READ_SAMPLE_INTERVAL/1000)

		rs = rs / self.READ_SAMPLE_TIMES

		return rs

	def MQResistanceCalculation(self):
		"""****************** MQResistanceCalculation ****************************************
		Input:   raw_adc - raw value read from adc, which represents the voltage
		Output:  the calculated sensor resistance
		Remarks: The sensor and the load resistor forms a voltage divider. Given the voltage
		         across the load resistor and its resistance, the resistance of the sensor
		         could be derived.
		************************************************************************************"""
		raw_value = float(self.MCP3008.getValue(self.MQ_CHANNEL))

		if raw_value > 0:
			#value_resistance = ( ( float(self.RL_VALUE) * (1023.0 - raw_value) / raw_value ) )
			value_resistance = ( ( float(self.RL_VALUE) * (1023.0 - raw_value) / raw_value ) )
			return value_resistance
		else:
			return 0

	def MQGetPercentage(self, rs_ro_ratio, pcurve):
		"""*****************************  MQGetPercentage **********************************
		Input:   rs_ro_ratio - Rs divided by Ro
		         pcurve      - pointer to the curve of the target gas
		Output:  ppm of the target gas
		Remarks: By using the slope and a point of the line. The x(logarithmic value of ppm) 
		         of the line could be derived if y(rs_ro_ratio) is provided. As it is a 
		         logarithmic coordinate, power of 10 is used to convert the result to non-logarithmic 
		         value.
		************************************************************************************"""
		#return pow(10, ( ( ( math.log10(rs_ro_ratio) - pcurve[1] ) / pcurve[2] ) + pcurve[0] ))
		return (pcurve[0] * pow((rs_ro_ratio), pcurve[1]))


class MQ_2(MQ_XX):
	def __init__(self, mcp3008, channel, resistance, clean_air_factor):
		MQ_XX.__init__(self, mcp3008, channel, resistance, clean_air_factor)
																			
		self.LPGCurve = [594.9230257, -2.144134195]													
		self.H2Curve = [1004.745073, -2.079457045]													
		self.COCurve = [39016.20807, -3.215094174]													
		self.SmokeCurve = [3960.712515, -2.312747132]	
													
	def MQGetGasPercentage(self, gas_id):
		"""*****************************  MQGetGasPercentage **********************************
		Input:   rs_ro_ratio - Rs divided by Ro
		         gas_id      - target gas type
		Output:  ppm of the target gas
		Remarks: This function passes different curves to the MQGetPercentage function which 
		         calculates the ppm (parts per million) of the target gas.
		************************************************************************************"""
		rs_ro_ratio = self.MQRead() / self.RO

		if gas_id == "GAS_LPG":
			return self.MQGetPercentage(rs_ro_ratio, self.LPGCurve)
		elif gas_id == "GAS_H2":
			return self.MQGetPercentage(rs_ro_ratio, self.H2Curve)
		elif gas_id == "GAS_CO":
			return self.MQGetPercentage(rs_ro_ratio, self.COCurve)
		elif gas_id == "GAS_SMOKE":
			return self.MQGetPercentage(rs_ro_ratio, self.SmokeCurve)
		else:
			return 0

class MQ_3(MQ_XX):
	def __init__(self, mcp3008, channel, resistance, clean_air_factor):
		MQ_XX.__init__(self, mcp3008, channel, resistance, clean_air_factor)
																			
		self.AlcoholCurve = [0.3994142455, -1.468637559]
		self.BenzineCurve = [4.880609598, -2.684999487]
													
	def MQGetGasPercentage(self, gas_id):
		"""*****************************  MQGetGasPercentage **********************************
		Input:   rs_ro_ratio - Rs divided by Ro
		         gas_id      - target gas type
		Output:  ppm of the target gas
		Remarks: This function passes different curves to the MQGetPercentage function which 
		         calculates the ppm (parts per million) of the target gas.
		************************************************************************************"""
		rs_ro_ratio = self.MQRead() / self.RO

		if gas_id == "GAS_ALCOHOL":
			return self.MQGetPercentage(rs_ro_ratio, self.AlcoholCurve)
		elif gas_id == "GAS_BENZINE":
			return self.MQGetPercentage(rs_ro_ratio, self.BenzineCurve)
		else:
			return 0

class MQ_4(MQ_XX):
	def __init__(self, mcp3008, channel, resistance, clean_air_factor):
		MQ_XX.__init__(self, mcp3008, channel, resistance, clean_air_factor)
																			
		self.CH4Curve = [1025.64421, -2.704016447]
		self.LPGCurve = [3854.967186, -3.060184212]
													
	def MQGetGasPercentage(self, gas_id):
		"""*****************************  MQGetGasPercentage **********************************
		Input:   rs_ro_ratio - Rs divided by Ro
		         gas_id      - target gas type
		Output:  ppm of the target gas
		Remarks: This function passes different curves to the MQGetPercentage function which 
		         calculates the ppm (parts per million) of the target gas.
		************************************************************************************"""
		rs_ro_ratio = self.MQRead() / self.RO

		if gas_id == "GAS_CH4":
			return self.MQGetPercentage(rs_ro_ratio, self.CH4Curve)
		elif gas_id == "GAS_LPG":
			return self.MQGetPercentage(rs_ro_ratio, self.LPGCurve)
		else:
			return 0


if __name__ == "__main__":
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)	

	mcp = MCP3008(1)

	MQ_2 = MQ_2(mcp, 0, 5, 9.83)  # MCP, CHANNEL, RESISTANCE, CLEAN_AIR_FACTOR
	#MQ_3 = MQ_3(mcp, 0, 5, 60)  # MCP, CHANNEL, RESISTANCE, CLEAN_AIR_FACTOR
	#MQ_4 = MQ_4(mcp, 0, 5, 4.4)  # MCP, CHANNEL, RESISTANCE, CLEAN_AIR_FACTOR
	#MQ_5 = MQ_5(mcp, 0, 5, 6.5)  # MCP, CHANNEL, RESISTANCE, CLEAN_AIR_FACTOR

	print("Calibrating...")
	MQ_2.MQCalibration()
	#MQ_3.MQCalibration()
	#MQ_4.MQCalibration()
	#MQ_5.MQCalibration()
	print("Calibration done.")
	#print("Ro = {0:.2f} kOhms".format(MQ_3.RO))

	while True:
		print("LPG : {} ppm | H2 : {} ppm | CO : {} ppm | SMOKE : {} ppm".format(int(MQ_2.MQGetGasPercentage( "GAS_LPG" )), int(MQ_2.MQGetGasPercentage( "GAS_H2" )), int(MQ_2.MQGetGasPercentage( "GAS_CO" )), int(MQ_2.MQGetGasPercentage( "GAS_SMOKE" ))))
		#print("Alcohol : {} mg/L | Benzine : {} mg/L".format(int(MQ_3.MQGetGasPercentage( "GAS_ALCOHOL" )), int(MQ_3.MQGetGasPercentage( "GAS_BENZINE" ))))
		#print("CH4 : {} ppm | LPG : {} ppm".format(int(MQ_4.MQGetGasPercentage( "GAS_CH4" )), int(MQ_4.MQGetGasPercentage( "GAS_LPG" ))))
		#print("CH4 : {} ppm | LPG : {} ppm".format(int(MQ_4.MQGetGasPercentage( "GAS_CH4" )), int(MQ_4.MQGetGasPercentage( "GAS_LPG" ))))

		time.sleep(0.5)

	GPIO.cleanup()

