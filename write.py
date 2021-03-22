#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import configparser
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
		hex_filename = sys.argv[1]

	bl = stm32bootloader(comport)
	if bl.init() < 0:
		return 1  # error
	if 0 != bl.set_loadermode():
		print('boot loaderに同期できません。')
		return 1  # error
	# ---------------------------------------------------------------
	print('blank checking...', end='')
	mem = bl.ReadMemory(0x08000000, 0x100)
	for b in mem:
		if b != 255:
			bl.FlashDump()
			print('write.py:フラッシュメモリーが消去されていません。')
			return 1  # error
	print('OK.')
	try:
		ih = IntelHex(hex_filename)
	except FileNotFoundError:
		print('ファイルが見つかりません [{}]'.format(hex_filename))
		return 1  # error
	file_buf = ih.tobinarray()
	bl.WriteMemory(0x08000000, file_buf)
	return 0  # no error


if __name__ == '__main__':
	ans = main()
	sys.exit(ans)

