#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time
import bootloader_uart as bl

def main():
	print('--------------------------------------')
	bl.disp_SourceLine( 'START', sys._getframe())
	bl.FlashDump()
	return

if __name__ == '__main__':
	main()

