#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time
import hashlib
import configparser
#import bootloader_can as bl
import bootloader_uart as bl

def main():
	print('--------------------------------------')
	add = 0x08000000
	buf = bl.ReadMemoryQuiet( add, 0x100 )
	bl.dump(add, buf )
	print('Program start')
	bl.ProgramStart()

	return

if __name__ == '__main__':
	bl.clear_sio()
	main()

