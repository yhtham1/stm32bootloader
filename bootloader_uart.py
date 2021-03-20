#! /usr/bin/python3
# -*- coding: utf-8 -*-
#ＵＴＦ８
"""
STM32 BootLoaderのライブラリ

20/06/07(日) 00:40:29
20/09/16(水) 15:03:02 STM32F103対応

"""
import os
import sys
import time
from dump import dump
import serial
import configparser

ACK = b'\x79'
NAK = b'\x1f'
inifile = configparser.ConfigParser()
inifile.read('bootloader.ini')
COMPORT  = inifile.get('settings', 'comport'  )
BAUDRATE = inifile.get('settings', 'baudrate' )

ERASE_CMD = 0x44
CMD_LIST = []
CMD_TTL = ( 
	'Version',
	'Get',
	'Get Version and ReadProtection',
	'Get ID',
	'Read Memory',
	'Go',
	'Write Memory',
	'Erase',
	'Write Protect',
	'Write Unprotect',
	'Readout Protect',
	'Readout Unprotect',
	'ACK'
)


UART = []


def showPort():
	print('COMPORT:{}'.format(UART.port))

"""
	disp_SourceLine( 'ERR', sys._getframe())
"""
def disp_SourceLine(msg, a):
	name = a.f_code.co_name
	line = a.f_code.co_firstlineno
	fn   = os.path.basename(a.f_code.co_filename)
	print('{} {}()@{} Line:{}'.format(msg, name, fn, line))


def siowrite(b):
	UART.write(b)

def wait1ms(n):
	time.sleep(n*1e-3)


def trim(bdat):
	for c in bdat:
		ans += c
	return ans


def disp_serial(UART):
	print('COMPORT:{} BAUD:{} parity:{}'.format(
		UART.port, UART.baudrate, UART.parity	)
	)


def setParityNone():
	global UART
	UART.close()
	UART.parity=serial.PARITY_NONE
	UART.open()
	print('setParityNone:', end='')
	disp_serial(UART)


def setParityEven():
	global UART
	UART.close()
	UART.parity=serial.PARITY_EVEN
	UART.open()
	disp_serial(UART)


####################################################################
def clear_rxq(t=0.02):
	UART.timeout = t
	while True:
		c = UART.read()
		if 0 == len(c):
			time.sleep(0.002)
			# print(' OK',end='')
			break
		else:
			time.sleep(0.002)
			print(' {:02X}'.format(c[0]),end='')
	#print('')


####################################################################
def wait_ack():
	UART.timeout = 0.01
	ct = 0
	while True:
		c = UART.read()
		if 1 == len(c):
			UART.timeout = 0.5
			print('')
			return c
		print('\rwait_ack {:5}'.format(ct), end='')
		ct += 1


####################################################################
def getIDN():
	siowrite('*IDN?\r\n'.encode('utf-8'))
	b_ans = UART.read(250)
	k_ans = b_ans.decode('utf-8')
	ans = k_ans.strip('\r\n')
	return ans


####################################################################
def append_checksum( c ):
	ans = 0
	for i in range(len(c)):
		ans ^= c[i]
#		print(i,'{:02X}'.format(ans))
	c.append( ans )
	return c

def make_address( add ):
	ans = bytearray()
	a1 = (add >> 24) & 0xff
	a2 = (add >> 16) & 0xff
	a3 = (add >> 8 ) & 0xff
	a4 = (add      ) & 0xff
	ans.append(a1)
	ans.append(a2)
	ans.append(a3)
	ans.append(a4)
	return ans


####################################################################
def cmdGet(display=True):
	global CMD_LIST
	CMD_LIST = []
	cmd = 0x00
	clear_rxq()
	ans = []
	siowrite(bytearray([cmd,0xff ^ cmd]))
	c = UART.read()
	if c == NAK:
		print('ERR1a {:02X}'.format( c[0]))
		return c[0]
	if c == ACK:
		c = UART.read()
		n = c[0]
		#print('--------------- cmdGet() -------------')

		for i in range(n+1):
			c = UART.read()
			#print('{:2} {:>30} : 0x{:02X}'.format(i, CMD_TTL[i], c[0]))
			CMD_LIST.append(c[0])
			ans.append( c[0] )
		c = UART.read()
	else:
		return None
	if True==display:
		print('--------------------------------------')
		for i in range(len(ans)):
			print("{:>30} : 0x{:02X}".format(CMD_TTL[i], ans[i]))
		print('--------------------------------------')
	return ans

####################################################################
def cmdGetID():
	UART.timeout=0.1
	clear_rxq()
	cmd = CMD_LIST[3]
	siowrite(bytearray([cmd,0xff ^ cmd]))
	c = UART.read()
	if c != ACK:
		print('cmdGetID():ERR1')
		return
	if c == ACK:
		c = UART.read()
		n = c[0]
		print('bytes {}'.format(n))
		for i in range(n+1):
			c = UART.read()
			print('{:28}:{:02X}'.format(MCD_TTL[i], c[0]))
		c = UART.read()
		if c == ACK:
			pass
		else:
			print('ERR3')
	else:
		print('ERR2')
	print('--------------------------------------')


####################################################################
def cmdReadMemory(add, length):
	UART.timeout=0.1
	cmd = CMD_LIST[4]
	siowrite(bytearray([cmd,0xff ^ cmd]))
	c = UART.read()
	if c != ACK:
		print('cmdReadMemory():{:02X} ERR1', c[0])
		return
	siowrite(append_checksum(make_address(add)))
	c = UART.read()
	if c != ACK:
		print('cmdReadMemory():{:02X} ERR2', c[0])
		return
	len1 = length-1
	siowrite( bytearray([len1, 0xff ^ len1]))
	c = UART.read()
	if c != ACK:
		print('cmdReadMemory():{:02X} ERR3', c[0])
		return
	ans = bytearray(b'')
	for i in range(length):
		c = UART.read()
		ans.append(c[0])
	return ans


####################################################################
def cmdGo(add):
	UART.timeout=0.1
	clear_rxq()
	cmd = CMD_LIST[5]
	siowrite(bytearray([cmd,0xff ^ cmd]))
	c = UART.read()
	if c != ACK:
		print('cmdGo():{:02X} ERR1', c[0])
		return
	siowrite(append_checksum(make_address(add)))
	c = UART.read()
	if c != ACK:
		print('cmdGo():{:02X} ERR2', c[0])
		return
	print('cmdGo(0x{:08X}):OK'.format(add))


####################################################################
def cmdWriteMemory(add, dat):
	UART.timeout=0.1
	cmd = CMD_LIST[6]
	siowrite(bytearray([cmd,0xff ^ cmd]))
	length = len(dat)
	c = UART.read()
	if c != ACK:
		print('cmdWriteMemory():0x{:02X} ERR1'.format(c[0]))
		return
	siowrite(append_checksum(make_address(add)))
	c = UART.read()
	if c != ACK:
		print('cmdWriteMemory():0x{:02X} ERR2'.format(c[0]))
		return
	len1 = length-1
	dat2 = bytearray([len1])
	dat2 += dat
	dat3 = append_checksum(dat2)
	siowrite(dat3)
	c = UART.read()
	if c != ACK:
		print('cmdWriteMemory():0x{:02X} ERR3'.format(c[0]))
		return
	else:
		pass
#		print('cmdWriteMemory(): OK')
	return


####################################################################
def cmdErase():
	UART.timeout=0.1
	cmd = CMD_LIST[7]
	siowrite(bytearray([cmd,0xbc]))
	c = UART.read()
	if c != ACK:
		print('cmdErase0x43():0x{:02X} ERR1'.format(c[0]))
		return

	dat2 = bytearray([0xff,0x00])
	print(dat2)
	siowrite(dat2)
	c = wait_ack()
	if c != ACK:
		print('cmdErase0x43():0x{:02X} ERR2'.format(c[0]))
		return
	return


####################################################################
def ReadMemory_sub(add, length, tick_char):
	clear_rxq()
	add1 = add
	num1 = length
	ans = bytearray(b'')
	while 256 < num1:
		sz = 256
		print(tick_char, end='')
		sys.stdout.flush()
		bk = cmdReadMemory(add1,    sz )
		ans += bk
		add1 += sz
		num1 -= sz
	if len(tick_char):
		print('')
	if num1 <= 0:
		return ans
	bk = cmdReadMemory(add1,    num1 )
	ans += bk
	return ans


def ReadMemory(add, length):
	return ReadMemory_sub(add, length, '*')


def ReadMemoryQuiet(add, length):
	return ReadMemory_sub(add, length, '')


def WriteMemory(baseadd, dat):
	clear_rxq()
	UART.timeout=0.1
	length = len(dat)
	add1 = 0
	num1 = length
	ans = bytearray(b'')
	bk = bytearray(256)
	while 256 < num1:
		sz = 256
		for i in range(sz):
			bk[i] = dat[i+add1]
#		print('*', end='')
		print('--------------------------- {:08X}'.format(baseadd+add1))
		dump(baseadd+add1, bk )
		cmdWriteMemory(baseadd+add1, bk )
		add1 += sz
		num1 -= sz
	if 0 < num1:
		bk1 = bytearray(num1)
		for i in range(num1):
			bk1[i] = dat[add1+i]
		print('\r--------------------------- {:08X}'.format(baseadd+add1))
		dump( baseadd+add1, bk1 )
		cmdWriteMemory(baseadd+add1, bk1 )
	print('')
	return


######################## 0x7fを送ってNAKが返るまで繰り返す
def sync():
	clear_rxq()
	UART.timeout=0.1
	#print('------------ SYNC START ---------')
	while True:
		siowrite(bytearray([0x7f]))
		time.sleep(0.001)
		c = UART.read()
		if 1 == len(c):
			if NAK == c:
				#print('------------ SYNC OK ------------')
				return

def ProgramStart():
	jmp = ReadMemoryQuiet( 0x08000004, 4 )
	dump( 0x08000004, jmp )
	add = 0
	add <<= 8
	add |= jmp[3]
	add <<= 8
	add |= jmp[2]
	add <<= 8
	add |= jmp[1]
	add <<= 8
	add |= jmp[0]
	if 0xffffffff == add:
		print('ProgramStart():ERROR add: {:08X}'.format(add))
		return

	# print('add: {:08X}'.format(add))
	cmdGo(add)


def disp0x10( add ):
	buf = ReadMemoryQuiet( add, 0x10 )
	dump(add, buf )

def BootDump():
	add = 0x08000000
	len1 = 0x800
	b = ReadMemoryQuiet( add, len1 )
	dump( add, b )


def init(): # 0: OK -1:NG
	global UART
	#----------------------------------------------------------
	try:
		UART = serial.Serial(
			port=COMPORT,
			baudrate=BAUDRATE,
			parity=serial.PARITY_EVEN,
	#		parity=serial.PARITY_NONE,
			timeout=0.5 )
	except:
		print('COMポートを使用できません。[{}]'.format(COMPORT))
		return -1
	clear_rxq()
	setParityEven()
	sync()
	cmdGet(True)
	#print('READY uart_bootloader.init()')
	disp_SourceLine( 'Ready', sys._getframe())
	return 0


def FlashDump():
	disp0x10( 0x08000000 )
	disp0x10( 0x08004000 )
	disp0x10( 0x08008000 )
	disp0x10( 0x0800c000 )
	disp0x10( 0x08010000 )
#	disp0x10( 0x08020000 )
#	disp0x10( 0x08040000 )
#	disp0x10( 0x08060000 )
#	disp0x10( 0x08080000 )
#	disp0x10( 0x080a0000 )
#	disp0x10( 0x080c0000 )
#	disp0x10( 0x080e0000 )


def main():
	#---------------------------------------------------------------
	if 0 == init():
		FlashDump()
	return

#----------------------------------------------------------
if __name__ == '__main__':
	main()



