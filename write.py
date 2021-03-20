#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time
from intelhex import IntelHex
import bootloader_can as bl


def main():
	print('-------------------------------------------------------- START {}'.format(sys.argv[0]))
	hex_filename= 'template.hex'
	if 2 == len(sys.argv):
		bin_filename = sys.argv[1]

	bl.setParityEven()
	#---------------------------------------------------------------
	print('blank checking...',end='')
	mem = bl.ReadMemory( 0x08000000, 0x100 )
	for b in mem:
		if b != 255:
			bl.FlashDump()
			print('write.py:BLANK CHECK ERROR')
			return
	print('OK.')
	return
	print('{} FILENAME:{}'.format(sys.argv[0], bin_filename))
	with open(bin_filename, 'rb') as f:
		buf1 = f.read()
	bl.WriteMemory( 0x08000000, buf1 )
#	bl.FlashDump()
	bl.BootDump()

	return

if __name__ == '__main__':
	bl.clear_sio()
	main()

