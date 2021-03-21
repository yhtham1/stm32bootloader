#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import configparser
import time
from bootloader_uart import stm32bootloader


def main():
	inifile = configparser.ConfigParser()
	inifile.read('bootloader.ini')
	comport = inifile.get('settings', 'comport')
	baudrate = inifile.get('settings', 'baudrate')
	print('--------------------------------------')
	bl = stm32bootloader(comport)
	if 0 == bl.init():
		bl.BootDump()
	sys.exit(0)
	return

if __name__ == '__main__':
	main()

