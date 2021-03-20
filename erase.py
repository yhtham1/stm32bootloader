#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time
import hashlib
import configparser
import bootloader as bl

def main():
	print('-------------------------------------------------------- START {}'.format(sys.argv[0]))
	bl.cmdEraseAll()

	return

if __name__ == '__main__':
	bl.clear_sio()
	main()

