#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time
import struct
from intelhex import IntelHex
import bootloader_can as bl

def maketest():
	parm=bytearray(0)
	for i in range(0x20004000, 0x2000c000, 4 ):
		#print('{:08X}'.format(i))
		parm += struct.pack('>L',i)
	return parm

def main():
	bl.init()
	#bl.cmdGet()
	mem = maketest()
	bl.dump(0x20004000, mem)
#	with open('test.bin','wb') as f:
#		f.write(mem)

	add = 0x20004000
	bl.WriteMemory( add, mem)
	mem = bl.ReadMemory( 0x20004000, 0x100 )
	bl.dump( 0x0000, mem )
	return

if __name__ == '__main__':
	main()

