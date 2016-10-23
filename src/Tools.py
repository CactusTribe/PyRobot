from math import *

class Tools:

	# Calcule la température en degrés kevlin
	def temp_kelvin(val):
		U = 3.3             # Tension d’alimentation du pont diviseur
		R = 1000            # Résistance en haut du pont
		B = 3730.0          # Constante de la thermistance
		T0 = 273.15 + 25    # Température de référence
		R0 = 1000.0         # Résistance de référence de la thermistance
		Ut = U - val 				# Tension mesurée avec l’entrée analogique

		return 1 / ( ( log( ( ( Ut * R / U ) / ( 1 - ( Ut / U ) ) ) / R0 ) / B ) + ( 1 / T0 ) ) # calibration


	# Calcule la température en degrés celcius
	def temp(val):
		return Tools.temp_kelvin(val) - 273

if __name__ == "__main__":
	#Tools.AnalogToCelsius(3.3)
	kelvin = Tools.temp_kelvin(512)
	celsius = Tools.temp(kelvin)

	print("Temp = {} K {} °C".format(kelvin, celsius))