import socket, sys, subprocess, time, threading, math
import RPi.GPIO as GPIO

from MCP3008 import MCP3008

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
		self.CALIBRATION_SAMPLE_INTERVAL = 300	# define the time interal(in milisecond) between each samples in the
																						# cablibration phase
		self.READ_SAMPLE_TIMES = 5							# define how many samples you are going to take in normal operation
		self.READ_SAMPLE_INTERVAL = 50 					# define the time interal(in milisecond) between each samples in 
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

	def MQResistanceCalculation(self):
		"""****************** MQResistanceCalculation ****************************************
		Input:   raw_adc - raw value read from adc, which represents the voltage
		Output:  the calculated sensor resistance
		Remarks: The sensor and the load resistor forms a voltage divider. Given the voltage
		         across the load resistor and its resistance, the resistance of the sensor
		         could be derived.
		************************************************************************************"""
		raw_value = self.MCP3008.getValue(self.MQ_CHANNEL)
		#print(raw_value_Volts)

		if raw_value > 0:
			#value_resistance = ( ( float(self.RL_VALUE) * (1023 - raw_value) / raw_value ) )
			value_resistance = ( float(self.RL_VALUE) / (1023 / raw_value - 1) )
			return value_resistance
		else:
			return 0

	def MQRead(self):
		"""*****************************  MQRead *********************************************
		Input:   mq_pin - analog channel
		Output:  Rs of the sensor
		Remarks: This function use MQResistanceCalculation to caculate the sensor resistenc (Rs).
		         The Rs changes as the sensor is in the different consentration of the target
		         gas. The sample times and the time interval between samples could be configured
		         by changing the definition of the macros.
		************************************************************************************"""
		i = 0
		rs = 0

		for e in range(self.READ_SAMPLE_TIMES):
			rs += self.MQResistanceCalculation()
			time.sleep(self.READ_SAMPLE_INTERVAL/1000)

		rs = rs / self.READ_SAMPLE_TIMES

		return rs

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
		return pow( 10 , ( ( ( math.log(rs_ro_ratio) - pcurve[1] ) / pcurve[2] ) + pcurve[0] ) )

class MQ_2(MQ_XX):
	def __init__(self, mcp3008, channel, resistance, clean_air_factor):
		MQ_XX.__init__(self, mcp3008, channel, resistance, clean_air_factor)

		self.LPGCurve = [2.3, 0.21, -0.47]		# two points are taken from the curve. 
																							# with these two points, a line is formed which is "approximately equivalent"
																							# to the original curve. 
																							# data format:{ x, y, slope}; point1: (lg200, 0.21), point2: (lg10000, -0.59) 
		self.COCurve = [2.3, 0.72, -0.34]		# two points are taken from the curve. 
																							# with these two points, a line is formed which is "approximately equivalent" 
																							# to the original curve.
																							# data format:{ x, y, slope}; point1: (lg200, 0.72), point2: (lg10000,  0.15) 
		self.SmokeCurve = [2.3, 0.53, -0.44]		# two points are taken from the curve. 
																							# with these two points, a line is formed which is "approximately equivalent" 
																							# to the original curve.
																							# data format:{ x, y, slope}; point1: (lg200, 0.53), point2: (lg10000,  -0.22) 

	def MQGetGasPercentage(self, gas_id):
		"""*****************************  MQGetGasPercentage **********************************
		Input:   rs_ro_ratio - Rs divided by Ro
		         gas_id      - target gas type
		Output:  ppm of the target gas
		Remarks: This function passes different curves to the MQGetPercentage function which 
		         calculates the ppm (parts per million) of the target gas.
		************************************************************************************"""
		rs_ro_ratio = self.MQRead() / self.RO
		print("RS = {0:.1f} kOhms".format(self.MQRead()))
		print("RS / RO = {}".format(rs_ro_ratio))

		if gas_id == "GAS_LPG":
			return self.MQGetPercentage(rs_ro_ratio, self.LPGCurve)
		elif gas_id == "GAS_CO":
			return self.MQGetPercentage(rs_ro_ratio, self.COCurve)
		elif gas_id == "GAS_SMOKE":
			return self.MQGetPercentage(rs_ro_ratio, self.SmokeCurve)
		else:
			return 0


if __name__ == "__main__":
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)	
	GPIO.cleanup()

	MCP3008 = MCP3008(12, 16, 20, 21) 	# PIN : CLK, MOSI, MISO, CS
	MQ_2 = MQ_2(MCP3008, 0, 1, 9.83)  # MCP, CHANNEL, RESISTANCE, CLEAN_AIR_FACTOR

	print("Calibrating...")
	MQ_2.MQCalibration()
	print("Calibration done.")
	print("Ro = {0:.1f} kOhms".format(MQ_2.RO))
	print("LPG = {0:.3f} ppm".format(MQ_2.MQGetGasPercentage( "GAS_LPG" )))

	GPIO.cleanup()

