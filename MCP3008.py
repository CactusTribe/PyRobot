#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time, sys
import RPi.GPIO as GPIO

DEBUG = 1

class MCP3008:
    def __init__(self, clockpin, mosipin, misopin, cspin):
        # Broches connectées sur l'interface SPI du MCP3008 depuis le Cobbler
        # (changer selon vos besoins)
        self.SPICLK = clockpin
        self.SPIMISO = misopin
        self.SPIMOSI = mosipin
        self.SPICS = cspin

        # Initialisation de l'interface SPI
        GPIO.setup(self.SPIMOSI, GPIO.OUT)
        GPIO.setup(self.SPIMISO, GPIO.IN)
        GPIO.setup(self.SPICLK, GPIO.OUT)
        GPIO.setup(self.SPICS, GPIO.OUT)

    # Lit les données SPI d'une puce MCP3008, 8 canaux disponibles (adcnum de 0 à 7)
    def readadc(self, adcnum, clockpin, mosipin, misopin, cspin ):
        if( (adcnum > 7) or (adcnum < 0)):
                return -1

        GPIO.output( cspin, True )

        GPIO.output( clockpin, False ) # met Clock à Low
        GPIO.output( cspin, False )    # met CS à Low (active le module MCP3008)

        commandout = adcnum # numéro de channel
        commandout |= 0x18  # OR pour ajouter Start bit + signle-ended bit
                            # 0x18 = 24d = 00011000b
        commandout <<=3     # décalage de 3 bits à gauche

        # Envoi des Bits sur le bus SPI
        for i in range(5):
                # faire un AND pour determiner l'état du bit de poids le plus 
                # fort (0x80 = 128d = 10000000b)
                if( commandout & 0x80 ): # faire un AND pour déterminer l'état du bit
                        GPIO.output( mosipin, True )
                else:
                        GPIO.output( mosipin, False )
                commandout <<= 1 # décalage de 1 bit sur la gauche

                # Envoi du bit mosipin avec signal d'horloge
                GPIO.output( clockpin, True )
                GPIO.output( clockpin, False )

        # lecture des bits renvoyés par le MCP3008
        # Lecture de 1  bit vide, 10 bits de données et un bit null
        adcout = 0
        for i in range(12):
                # Signal d'horloge pour que le MCP3008 place un bit
                GPIO.output( clockpin, True )
                GPIO.output( clockpin, False )
                # décalage de 1 bit vers la gauche
                adcout <<= 1
                # stockage du bit en fonction de la broche miso
                if( GPIO.input(misopin)):
                        adcout |= 0x1 # active le bit avec une opération OR

        # Mettre Chip Select à High (désactive le MCP3008)
        GPIO.output( cspin, True )

        # Le tout premier bit (celui de poids le plus faible, le dernier lut)
        # est null. Donc on l'elimine ce dernier bit en décalant vers la droite
        adcout >>= 1

        return adcout

    def getValue(self, channel):
        if channel < 8 and channel >= 0:
            value = self.readadc( channel, self.SPICLK, self.SPIMOSI, self.SPIMISO, self.SPICS )
            return value

    def read(self, channel, timer):
        start = time.time()
        elapsed = 0

        while True:
            # pour une valeur de tension entre 0 et VRef (3.3v)
            value = MCP3008.getValue(sensor_ch)

            sys.stdout.write("\r CH #"+str(sensor_ch)+" Valeur: {0:.2f} ({1:.2f} Volt)".format( value, (3.3*value)/1024 ) )
            sys.stdout.flush()
            time.sleep(0.5) 

            elapsed = time.time() - start
            if elapsed >= timer:
                break


if __name__ == "__main__":

    GPIO.setmode( GPIO.BCM )
    GPIO.setwarnings(False) 

    # CLK, MOSI, MISO, CS
    MCP3008 = MCP3008(12, 16, 20, 21)
    # Potentiomètre 10KOhms raccordés sur le canal ADC #0
    sensor_ch = 0
    MCP3008.read(sensor_ch, 10)
    print("")

    GPIO.cleanup()