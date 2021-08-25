#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

import configparser
import serial.tools.list_ports
import ft232
import time


def port_detail(p):
	print('----------------------------------------------------------')
	print('device       :{}'.format(p.device))
	print('name         :{}'.format(p.name))
	print('description  :{}'.format(p.description))
	print('hwid         :{}'.format(p.hwid))
	print('serial_number:{}'.format(p.serial_number))
	print('location     :{}'.format(p.location))
	print('manufacturer :{}'.format(p.manufacturer))
	print('product      :{}'.format(p.product))
	print('interface    :{}'.format(p.interface))


def get_serialnumber(target_port):
	target_port = target_port.upper()
	print('target={}'.format(target_port))
	ports = list(serial.tools.list_ports.comports())
	ans = None
	for it in ports:
		# port_detail(it)
		print('---------------------', it.name)
		if it.name.upper() == target_port:
			if None != it.serial_number:
				ans = it.serial_number[:-1]
				print('found:{}-{}'.format(target_port, ans))
			else:
				print('error')
		else:
			print('{} {} {}'.format(it.name.upper(), it.serial_number, it.manufacturer))
	return ans


# cusb bit0: NRST
# cusb bit1: BOOT0
# cusb bit2: BOOT1
# cusb bit3: PB14

# n:0 NORMAL BOOT
# n:1 BOOT LOADER
# n:2 not use
# n:3 RAM BOOT

def reboot(sp, n):
	pat = int(n * 2)
	sp.cbus_setup(mask=0x0f, init=pat)
	sp.cbus_write(pat)
	time.sleep(0.1)
	sp.cbus_setup(mask=0x0e, init=pat)


def main():
	inifile = configparser.ConfigParser()
	inifile.read('bootloader.ini')
	comport = inifile.get('settings', 'comport')
	serial_number = get_serialnumber(comport)

	i = 1
	boot_mode = 3
	while i < len(sys.argv):  # in range(1, len(sys.argv)):
		arg2 = sys.argv[i].strip()
		if 0 <= arg2.find('--port'):
			comport = sys.argv[i + 1].strip()
			i += 2
			continue
		if 0 <= arg2.find('--mode'):
			boot_mode = int(sys.argv[i + 1].strip())
			continue
		i += 1

	if None == serial_number:
		print('serial_number not found')
		return
	print('target is {}'.format(serial_number))
	sp = []
	try:
		sp = ft232.Ft232(serial_number, baudrate=115200)
	except ft232.Ft232Exception:
		print("Unable to open the ftdi device: %s" % serial_number)
		sys.exit(1)

	reboot(sp, boot_mode)



	# You may use sp as you would a Serial object
	# sp.write(b"Hello World!\n")
	# resp = sp.read(100)

	# If you want to use the CBUS pins, you enable them with cbus_setup
	# 'mask' is a bitmask which specifies which pins to enable
	# 'init' is a bitmask for the initial value for each pin
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
