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
	if bl.init() < 0:
		return 1  # error
	if 0 != bl.set_loadermode():
		print('boot loaderに同期できません。')
		return 1  # error
	bl.BootDump()
	return 0  # no error

if __name__ == '__main__':
	ans = main()
	sys.exit(ans)
