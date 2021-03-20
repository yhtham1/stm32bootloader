#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import struct
import can
import time
from dump import dump
import RPi.GPIO as GPIO
import configparser
from datetime import datetime

"""
VER: 0x20	[ 0]
GETCMD: 0x00	[ 1]
GETVER: 0x01	[ 2]
GETID: 0x02	[ 3]
SPEED: 0x03	[ 4]
Read: 0x11	[ 5]
GOTO: 0x21	[ 6]
Write memory: 0x31	[ 7]
Erase memory: 0x43	[ 8]
Write Protect: 0x63	[ 9]
Write Unprotect: 0x73	[11]
Readout Protect: 0x82	[12]
Readout Unprotect: 0x92	[13]

can125 8bytes = 914uS

"""
inifile = configparser.ConfigParser()
inifile.read('bootloader.ini')
CANDEV = inifile.get('settings', 'candev' )
CANBUS = []
CODE_NAK = 0x1f
CODE_ACK = 0x79
CMD_TTL = (
	'Version',
	'Get',
	'Get Version and ReadProtection',
	'Get ID',
	'Speed',
	'Read memory',
	'Go',
	'Write memory',
	'Erase memory',
	'Write Protect',
	'Write Unprotect',
	'Readout Protect',
	'Readout Unprotect',
	'ACK'
)
DEBUG = 0

GPIO.setwarnings(False)
#GPIO.setmode(GPIO.BCM)		#CPUのGPIO名称
GPIO.setmode(GPIO.BOARD)	#コネクタピン番号

GPIO.setup( 38, GPIO.OUT)	#
GPIO.output(38,False)		#


CMD_LIST = []

"""
	disp_SourceLine( 'ERR', sys._getframe())
"""
def disp_SourceLine(msg, a):
	name = a.f_code.co_name
	line = a.f_code.co_firstlineno
	fn   = os.path.basename(a.f_code.co_filename)
	print('{} {}()@{} Line:{}'.format(msg, name, fn, line))


def wait1ms(ms):
	time.sleep(ms*0.001)
	return


def make_address( add ):# uint32 -> bytearray
	ans = struct.pack('>L',add)
	return ans


def can_send( stdid, dat ):
	try:
		msg0 = can.Message(arbitration_id=stdid, data=dat,extended_id=False)
		CANBUS.send(msg0)
	except:
		disp_SourceLine( 'ERR', sys._getframe())

def can125():
	os.system('sudo ip link set can0 down type can')
	os.system('sudo ip link set can0 type can bitrate 125000')
	os.system('sudo ip link set can0 type can restart-ms 100')
	os.system('sudo ip link set can0 up type can')

def can500():
	os.system('sudo ip link set can0 down type can')
	os.system('sudo ip link set can0 type can bitrate 500000')
	os.system('sudo ip link set can0 type can restart-ms 100')
	os.system('sudo ip link set can0 up type can')


####################################################################
def getrx(timeout=0.5):
	while True:
		ans =CANBUS.recv(timeout)
		if None != ans:
			if False == ans.is_error_frame:
				break
		else:
			return None
	return ans


def clear_rxq(t=0.05):
	ct = 0
	ans =CANBUS.recv(t)	#重要なタイミング
	while ans != None:
		ans =CANBUS.recv(t)
		ct += 1
	return ct


####################################################################
def sync():
	clear_rxq()
	can_send(0x79,None)
	a = getrx()
	if None == a:
		print('sync error0')
		return -1 # error
	if a.dlc==1:
		if CODE_ACK == a.data[0] or CODE_NAK == a.data[0]:
			return 0 # OK
		else:
			print('sync error {:02X}'.format(a.data[0]))
			return -1 # error
	return -1 # error

def printcan(rxdat):
	print('StdId:0x{:03X} DLC:{:d}-'.format(rxdat.arbitration_id,rxdat.dlc),end='')
	for dat in rxdat.data:
		print('{:02X} '.format(dat),end='')
	print(']')


def wait_ack(cmd):
	datok = 0
	ans = 0
	while 0 == datok:
		dat = getrx()
		if None == dat:
			disp_SourceLine( 'ERR timeout', sys._getframe())
			clear_rxq(1)
			return None
		if 1 == dat.dlc and cmd == dat.arbitration_id:
			ans = dat.data[0]
			datok=1
			# print(' ans:0x{:02X}'.format(ans))
			if CODE_ACK == ans:
				pass
			if CODE_NAK == ans:
				pass
		else:
			print('ERR wait_ack(150)=', end='')
			clear_rxq(1)
			printcan(dat)
			return None
	return ans

####################################################################
def WriteMemory(baseadd, dat):
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



####################################################################
def cmdGet(display=True):
	ans = []
	cmd = 0x00
	clear_rxq()
	can_send( cmd, dat=None )	#GET COMMAND
	if None==wait_ack(cmd):
		print('cmdGet():ERROR')
		return None
	d = getrx()	#1
	blen = d.data[0]
	for i in range(blen+1):
		d = getrx()
		ans.append( d.data[0] )
	wait_ack(cmd)
	clear_rxq()
	if True==display:
		print('--------------------------------------')
		for i in range(len(ans)):
			print("{:>30} : 0x{:02X}".format(CMD_TTL[i], ans[i]))
		print('--------------------------------------')
	return ans


####################################################################
def cmdGetID():
	clear_rxq()
	cmd = CMD_LIST[3]	# 0x02 CPUバージョンの取得
	ans = 0
	can_send( cmd, dat=None )
	wait_ack(cmd)
	d = getrx()
	wait_ack(cmd)
	if 2 != d.dlc:
		print('cmdGetID() ERROR')
		return None
	ans = struct.unpack( '>H',d.data)
#	print("CPU_ID:{:04X}".format(ans))
	return ans


####################################################################
def cmdSpeed(speed):
	global CANBUS
	cmd = CMD_LIST[4]	# 0x03 Speed
	ans = 0
	clear_rxq()
	dat = bytearray(1)
	dat[0] = 0x03 # speed 0x01:125k 0x02:250k 0x03:500k 0x04:1M
	can_send( cmd, dat )
	wait_ack(cmd)
	CANBUS.shutdown()
	print('sudo can500')
	can500()
	wait1ms(100)
	CANBUS = can.interface.Bus(channel = CANDEV, bustype='socketcan')
	wait1ms(100)
	wait_ack(cmd)
	return ans


####################################################################
def cmdReadMemory(add, len2):
	while 0 < clear_rxq(0.1):
		print('x')
	cmd = CMD_LIST[5]	# 0x11 Read Memory
	if 256 < len2:
		print('ERR cmdReadMemory({})'.format(len2))
	ans = bytes(b'')
	b1 = len2-1
#	parm = add.to_bytes(4,'big')
#	parm += b1.to_bytes(1,'big')
	parm = struct.pack('>L',add)	# to バイト列
	parm += struct.pack('>B',b1)	# to バイト列
	can_send(cmd, parm )							# コマンド送信
	wait1ms(50)										#低速時
	if None == wait_ack(cmd):						# コマンドACK
		print('ERR cmdReadMemory() wait_ack(274) error')
		clear_rxq(1)
		return None
	remain = len2
	GPIO.output( 38, True );
	while 0 < remain:
		a = getrx()
		if None == a:
			return None
		remain -= a.dlc
		ans += a.data
	GPIO.output( 38, False );
	if None == wait_ack(cmd):
		print('ERR cmdReadMemory() wait_ack(287) error')
		clear_rxq(1)
		return None
	return ans


####################################################################
def cmdGo(add):
	clear_rxq()
	cmd = CMD_LIST[6]	# 0x021 GOTO
	dat = make_address(add)
	print(dat)
	can_send( cmd, dat )
	wait_ack(cmd)


####################################################################
def cmdWriteMemory(add, blk):
	clear_rxq()
	cmd = CMD_LIST[7] # 0x31 Write Memory
	len2 = len(blk)
	if 256 < len2:
		print('ERR write_mem1({})'.format(len2))
	ans = bytes(b'')
	b1 = len2-1
	parm = struct.pack('>L',add)	# to バイト列
	parm += struct.pack('>B',b1)	# to バイト列
	can_send(cmd, parm )
	wait_ack(cmd)
	remain = len2
	wp = 0
	while 8 <= remain:
		can_send( cmd, blk[wp:wp+8])
		remain -= 8
		wp += 8
		wait_ack(cmd)
		clear_rxq()
	if 0 < remain:
		can_send( cmd, blk[wp:])
		print('last=',remain)
		wait_ack(cmd)
	return ans


####################################################################
def cmdEraseMemory():
	cmd = CMD_LIST[8]	# 0x43 EraseMemory
	ans = 0
	clear_rxq()
	can_send( cmd, [0xff] )
	wait_ack(cmd) #コマンドOK
	print('wait moment')
	wait_ack(cmd) #EraseOK
	return ans


def test_responce():
	can_send(0x79, None )
	t1 = time.time()
	wait1ms(100)
	t2 = time.time()




####################################################################
def ReadMemory_sub(add, length, tick_char):
	add1 = add
	num1 = length
	sz = length
	ans = bytearray(b'')
	while 256 < num1:
		sz = 256
		print(tick_char, end='')
		sys.stdout.flush()
		bk = cmdReadMemory(add1, sz )
		while None == bk:
			#print('ReadMemory_sub():retry')
			print('R', end='')
			sys.stdout.flush()
			bk = cmdReadMemory(add1, sz )
		ans += bk
		add1 += sz
		num1 -= sz
	if len(tick_char):
		print('')
	if num1 <= 0:
		return ans
	bk = cmdReadMemory(add1, num1 )
	while None == bk:
		print('ReadMemory_sub():retry 0x{:08X}-{}'.format(add1,sz))
		bk = cmdReadMemory(add1, sz )
	ans += bk
	return ans


def ReadMemory(add, length):
	return ReadMemory_sub(add, length, '*')


def ReadMemoryQuiet(add, length):
	return ReadMemory_sub(add, length, '')


def WriteMemory(baseadd, dat):
	clear_rxq()
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




####################################################################
def disp0x10( add ):
	buf = ReadMemoryQuiet( add, 0x10 )
	dump(add, buf )

def BootDump():
	add = 0x08000000
	len1 = 0x800
	b = ReadMemoryQuiet( add, len1 )
	dump( add, b )

def FlashDump():
	disp0x10( 0x08000000 )
	disp0x10( 0x08004000 )
	disp0x10( 0x08008000 )
	disp0x10( 0x0800c000 )
	disp0x10( 0x08010000 )
	disp0x10( 0x08020000 )
	disp0x10( 0x08040000 )
	disp0x10( 0x08060000 )
	disp0x10( 0x08080000 )
	disp0x10( 0x080a0000 )
	disp0x10( 0x080c0000 )
	disp0x10( 0x080e0000 )




def ProgramStart():
	clear_rxq()
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

	print('ProgramStart(0x{:08X})'.format(add))
	cmdGo(add)


####################################################################
def init(): # 0:OK -1:NG
	global CMD_LIST
	global CANBUS
	try:
		CANBUS = can.interface.Bus(channel = CANDEV, bustype='socketcan')
		#CANBUS = can.interface.ThreadSafeBus(channel = CANDEV, bustype='socketcan')
	except:
		return -1
	try:
		while 0 != sync():
			pass
		#	can_send( 0x79, None )	# start BootLoader
		wait1ms(100)
		CMD_LIST = cmdGet(False)
	except:
		disp_SourceLine( 'ERR', sys._getframe())
		return -1
	print('READY can_bootloader.init()')
	return 0

def setParityEven():
	pass

def clear_sio():
	pass


####################################################################
def main():

	if 0 == init():
		print('--------------------------------------')
		FlashDump()
		return

	CANBUS.shutdown()
	wait1ms(100)
	return


if __name__ == "__main__":
	main()


