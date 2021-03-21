#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from bootloader_uart import stm32bootloader

def main():
	print('-------------------------------------------------------- START {}'.format(sys.argv[0]))
	bl = stm32bootloader()
	bl.cmdErase()

	return

if __name__ == '__main__':
	main()

