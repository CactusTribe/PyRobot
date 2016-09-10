#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time, sys
import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

DEBUG = 1

class MCP3008:
    def __init__(self, device_num): # CE0 or CE1
        
        SPI_PORT = 0
        SPI_DEVICE = device_num
        self.mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

    def getValue(self, channel):
        if channel < 8 and channel >= 0:
            return self.mcp.read_adc(channel)
        else:
            return -1

    def readAll(self):
        print("Reading MCP3008 values, press Ctrl-C to quit...")
        print("| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |".format(*range(8)))
        print("-" * 57)

        while True:
            values = [0]*8
            for i in range(8):
                values[i] = self.getValue(i)

            sys.stdout.write("\r| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |".format(*values))
            sys.stdout.flush()
            time.sleep(0.5) 

if __name__ == "__main__":

    GPIO.setmode( GPIO.BCM )
    GPIO.setwarnings(False) 

    MCP3008_1 = MCP3008(0)
    #MCP3008_2 = MCP3008(1)


    MCP3008_1.readAll()
    #MCP3008_2.readAll()
    print("")

    GPIO.cleanup()