#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time
import hashlib
import configparser
from dump import dump
#import bootloader_can as bl
from bootloader_uart import stm32bootloader

def main():
	inifile = configparser.ConfigParser()
	inifile.read('bootloader.ini')
	comport = inifile.get('settings', 'comport')
	# baudrate = inifile.get('settings', 'baudrate')
	print('--------------------------------------')
	bl = stm32bootloader(comport)
	if 0 == bl.init():
		add = 0x08000000
		buf = bl.ReadMemoryQuiet( add, 0x100 )
		dump(add, buf )
		print('Program start')
		bl.ProgramStart()
		sys.exit(0)
		return
	sys.exit(1)
	return

if __name__ == '__main__':
	main()

