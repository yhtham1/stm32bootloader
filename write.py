#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import configparser
import time
import hashlib
from intelhex import IntelHex
from bootloader_uart import stm32bootloader


def main():
	inifile = configparser.ConfigParser()
	inifile.read('bootloader.ini')
	comport = inifile.get('settings', 'comport')
	# baudrate = inifile.get('settings', 'baudrate')
	print('-------------------------------------------------------- START {}'.format(sys.argv[0]))
	hex_filename = 'template.hex'
	if 2 == len(sys.argv):
		bin_filename = sys.argv[1]

	bl = stm32bootloader(comport)
	if bl.init() < 0:
		print('ERROR bl.init')
		sys.exit(1)
		return
	# ---------------------------------------------------------------
	print('blank checking...', end='')
	mem = bl.ReadMemory(0x08000000, 0x100)
	for b in mem:
		if b != 255:
			bl.FlashDump()
			print('write.py:BLANK CHECK ERROR')
			sys.exit(1)
			return
	print('OK.')
	fn = 'template.hex'
	ih = IntelHex(fn)
	file_buf = ih.tobinarray()
	bl.WriteMemory(0x08000000, file_buf)
	sys.exit(0)
	return


if __name__ == '__main__':
	main()
