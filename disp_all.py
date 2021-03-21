#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time
import configparser
from bootloader_uart import stm32bootloader

inifile = configparser.ConfigParser()
inifile.read('bootloader.ini')
comport = inifile.get('settings', 'comport')
baudrate = inifile.get('settings', 'baudrate')


def main():
	print('--------------------------------------')
	bl = stm32bootloader('com16')
	# bl.disp_SourceLine( 'START', sys._getframe())
	bl.FlashDump()
	return

if __name__ == '__main__':
	main()

