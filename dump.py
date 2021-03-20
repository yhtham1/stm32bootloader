#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

####################################################################
def putascii(c):
	if 0x20 <= c and c <= 0x7d:
		ans = '{:c}'.format(c)
	else:
		ans ='.'
	return ans

####################################################################
def dump16bytes(add, block16):
	ans = '{:08X}: '.format(add)
	ct = 16-len(block16)
	for d in block16:
		ans += '{:02X} '.format(d)
	ans += '   '
	for i in range(ct):
		ans += '   '
	for d in block16:
		ans += putascii(d)
	ans += '\n'
	return ans

####################################################################
def dump(dispadd, blockdata, title=False, out_text=False):
	remain = len(blockdata)
	i = 0
	ans = ''
	if title:
		a1 =  "-----------------------------------------------------------------------------\n"
		a1 += "           0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f    0123456789abcdef\n"
		if out_text:
			ans += a1
		else:
			print(a1,end='')
	while 0<remain:
		if 16<remain:
			sd = blockdata[i:i+16]
			a1 = dump16bytes(dispadd+i, sd)
			if out_text:
				ans += a1
			else:
				print(a1,end='')
			i += 16
			remain -= 16
		else:
			sd = blockdata[i:]
			a1 = dump16bytes(dispadd+i, sd)
			if out_text:
				ans += a1
			else:
				print(a1,end='')
			remain = 0
	return ans

####################################################################
def main():
	blk = bytearray(260)
	for i in range(len(blk)):
		blk[i] = 0xff & i
	ans = dump(0x08000000, blk, True, True )
	print(ans,end='')
	return

if __name__ == "__main__":
	main()


