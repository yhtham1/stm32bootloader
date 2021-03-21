#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time
import configparser
from bootloader_uart import stm32bootloader


def main():
	inifile = configparser.ConfigParser()
	inifile.read('bootloader.ini')
	comport = inifile.get('settings', 'comport')
	baudrate = inifile.get('settings', 'baudrate')
	print('--------------------------------------')
	bl = stm32bootloader(comport)
	if bl.init() < 0:
		sys.exit(1)
		return
	# bl.disp_SourceLine( 'START', sys._getframe())
	bl.FlashDump()
	sys.exit(0)
	return


if __name__ == '__main__':
	main()
