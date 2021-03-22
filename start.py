#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time
import hashlib
import configparser
from dump import dump
# import bootloader_can as bl
from bootloader_uart import stm32bootloader


def main():
	inifile = configparser.ConfigParser()
	inifile.read('bootloader.ini')
	comport = inifile.get('settings', 'comport')
	# baudrate = inifile.get('settings', 'baudrate')
	print('--------------------------------------')
	bl = stm32bootloader(comport)
	if bl.init() < 0:
		return 1  # error
	if 0 != bl.set_loadermode():
		print('boot loaderに同期できません。')
		return 1  # error
	add = 0x08000000
	buf = bl.ReadMemoryQuiet(add, 0x100)
	dump(add, buf)
	print('Program start')
	bl.ProgramStart()
	return 0  # no error


if __name__ == '__main__':
	ans = main()
	sys.exit(ans)
