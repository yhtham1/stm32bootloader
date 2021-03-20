#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time
#import bootloader_can as bl
import bootloader_uart as bl


def main():
	print('--------------------------------------')
	bl.BootDump()
	return

if __name__ == '__main__':
	main()

