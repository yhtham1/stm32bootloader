#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time
from intelhex import IntelHex
import hashlib
import configparser
# import bootloader_can as bl
from bootloader_uart import stm32bootloader

"""
21/02/20(土) 00:06:27
コンパイラの吐くバイナリーとIntelHexは違う。
IntelHexは、いくつかのセグメントに分かれるのでセグメント間はフラッシュ上で0xffとなる。
バイナリーファイルは0x00で埋まっている。

"""


def main():
	inifile = configparser.ConfigParser()
	inifile.read('bootloader.ini')
	comport = inifile.get('settings', 'comport')
	# baudrate = inifile.get('settings', 'baudrate')
	print('-------------------------------------------------------- START {}'.format(sys.argv[0]))
	bl = stm32bootloader(comport)
	if bl.init() < 0:
		sys.exit(1)
		return
	# ---------------------------------------------------------------
	fn = 'template.hex'
	ih = IntelHex(fn)
	file_buf = ih.tobinarray()
	file_size = len(file_buf)
	file_md5 = hashlib.md5(file_buf).hexdigest()

	flash_buf = bl.ReadMemory(0x08000000, file_size)
	flash_size = len(flash_buf)
	flash_md5 = hashlib.md5(flash_buf).hexdigest()
	print('{} {:7d} {}'.format(fn, file_size, file_md5))
	print('       FLASH {:7d} {}'.format(flash_size, flash_md5))
	with open('flash.bin', 'wb') as f:
		f.write(flash_buf)
	if flash_md5 != file_md5:
		sys.exit(1)  # ERROR
	else:
		sys.exit(0)  # OK
	return


if __name__ == '__main__':
	main()
