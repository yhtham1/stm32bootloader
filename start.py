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
	print('--------------------------------------')
	bl = stm32bootloader('com16')
	bl.init()
	add = 0x08000000
	buf = bl.ReadMemoryQuiet( add, 0x100 )
	dump(add, buf )
	print('Program start')
	bl.ProgramStart()

	return

if __name__ == '__main__':
	main()

