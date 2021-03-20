#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time
import serial
import hashlib
import configparser
import bootloader_uart as bl



def main():
	bl.setParityNone()
	bl.sio.write(b'\r')
	bl.wait1ms(100)
	bl.sio.write(b'\r')
	bl.wait1ms(100)
	bl.sio.write(b'selw:0\r')
	bl.wait1ms(100)
	bl.sio.write(b'GOTOW:900,900\r')
if __name__ == '__main__':
	main()

