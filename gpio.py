#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import struct
import can
import time
import RPi.GPIO as GPIO




####################################################################
def main():
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup( 38, GPIO.OUT)	# BUZZ
	GPIO.output(38,True)		# MOTOR CS1
	while True:
		time.sleep(1)
	return




if __name__ == "__main__":
	main()


