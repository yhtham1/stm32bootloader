#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

import configparser
import serial.tools.list_ports
import ft232
import time


def get_serialnumber(target_port):
	target_port = target_port.upper()
	# print(target_port)
	ports = list(serial.tools.list_ports.comports())
	ans = None
	for it in ports:
		if it.name.upper() == target_port:
			ans = it.serial_number[:-1]
			print('found:{}-{}'.format(target_port, ans))
		else:
			print('{} {} {}'.format(it.name.upper(), it.serial_number, it.manufacturer))
	return ans


def main():
	inifile = configparser.ConfigParser()
	inifile.read('bootloader.ini')
	comport = inifile.get('settings', 'comport')
	serial_number = get_serialnumber(comport)
	print(serial_number)
	sp = []
	try:
		sp = ft232.Ft232(serial_number, baudrate=115200)
	except ft232.Ft232Exception:
		print("Unable to open the ftdi device: %s" % serial_number)
		sys.exit(1)

	# You may use sp as you would a Serial object
	# sp.write(b"Hello World!\n")
	# resp = sp.read(100)

	# If you want to use the CBUS pins, you enable them with cbus_setup
	# 'mask' is a bitmask which specifies which pins to enable
	# 'init' is a bitmask for the initial value for each pin
	sp.cbus_setup(mask=15, init=1)
	# Change the current value of all setup pins
	sp.cbus_write(0)
	time.sleep(3)

	sp.cbus_setup(mask=14, init=0)
	return
	# while True:
	# 	sp.cbus_write(1)
	# 	time.sleep(0.1)
	# 	sp.cbus_write(2)
	# 	time.sleep(0.1)
	# 	sp.cbus_write(4)
	# 	time.sleep(0.1)
	# 	sp.cbus_write(8)
	# 	time.sleep(0.1)

	# Print the current value of all setup pins
	print("CBUS: %s" % sp.cbus_read())


if __name__ == '__main__':
	main()
