#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import can
import time
from dump import mini_dump
from queue import Queue

import threading
from concurrent.futures import ThreadPoolExecutor

RXQ = Queue()
TXQ = Queue()

fil = [{"can_id": 0x7fc, "can_mask": 0x7ff, "extended": False}]

bus = can.interface.Bus(channel = 'can0', bustype='socketcan',can_filters=fil)


QUIT_REQUEST = 0

class mycan_CallBackFunction(can.Listener):
	def on_message_received(self, msg):
		#print('callback RX',msg.arbitration_id, msg.dlc, msg.data)
		RXQ.put(msg)

def wait1ms(ms):
	time.sleep(ms*0.001)
	return


def can125():
	os.system('sudo ip link set can0 down type can')
	os.system('sudo ip link set can0      type can bitrate 125000')
	os.system('sudo ip link set can0      type can restart-ms 100')
	os.system('sudo ip link set can0 up   type can')

def can500():
	os.system('sudo ip link set can0 down type can')
	os.system('sudo ip link set can0      type can bitrate 500000')
	os.system('sudo ip link set can0      type can restart-ms 100')
	os.system('sudo ip link set can0 up   type can')

def printcan(candat):
	stdid = candat.arbitration_id;
	dlc   = candat.dlc
	print('TO:{:2d} FROM:{:2d} [{}] [ '.format(((stdid & 0x1f8)>>3),candat.data[0],candat.dlc ),end='')
	for dat in candat.data[2:]:
		print('{:02X} '.format(dat),end='')
	print(']')

def can_send( idn, dat ):
	#print('can_send(0x{:03X}) '.format(idn),end='' )
	msg0 = can.Message(arbitration_id=idn, data=dat,extended_id=False)
#	printcan(msg0)
	bus.send(msg0)

def clear_rxq():
	while not RXQ.empty():
		RXQ.get()
	return

def getrx():
	while RXQ.empty():
		return None
	ans = RXQ.get()
	return ans
	#print('getrx():internal error')


def send_cantel( toID, fromID, msg ):
	stdid = int(toID<<3)+0x600+0x04
	dat2 = bytearray(8)
	bmsg = msg.encode('utf-8')
	blen = len(bmsg)
	ix = 0
	while 0 < blen:
		if 6 < blen:
			len1 = 6
			dat1 = bmsg[ix:ix+len1]
		else:
			len1 = blen
			dat1 = bmsg[ix:ix+len1]
		dat2[0] = int(fromID) & 0x3f
		dat2[1] = 0x00
		dat2[2:] = dat1
#		print('canmsg:{:03X}#'.format(stdid),end='')
#		mini_dump(dat2)
		can_send( stdid, dat2 )
		blen -= len1
		ix += len1

def print_cantel(a):
	if a.arbitration_id == 0x7fc:
		bstr = a.data[2:a.dlc]
		print(bstr.decode('utf-8'),end='')
	else:
		print(a)


def txjob():
	while 0==QUIT_REQUEST:
		msg = input()
		msg += '\r'
		send_cantel( 0x00, 0x3f, msg )

def rxjob():
	while 0==QUIT_REQUEST:
		a = getrx()
		if None != a:
			print_cantel(a)
	return	

####################################################################
def main():
	# バスの初期化
	#bus = can.interface.Bus(channel = 'can0', bustype='socketcan', bitrate=250000, canfilters=None)
	# すでに用意されているコールバック関数(can.Listenerクラスのon_message_received関数)をオーバーライド
	call_back_function = mycan_CallBackFunction()		# コールバック関数のインスタンス生成
	can.Notifier(bus, [call_back_function, ])	# コールバック関数登録

#	print(bus.filters())
#	print(can.BusABC.filters())

	EXECUTOR = ThreadPoolExecutor(max_workers=4)

	thread1 = EXECUTOR.submit(txjob)
	thread2 = EXECUTOR.submit(rxjob)
	while( not(thread1.done() and thread2.done())):
		time.sleep(1)
	return
	print('start cantel terminal')
	try:
		thread1 = EXECUTOR.submit(txjob)
		thread2 = EXECUTOR.submit(rxjob)
		while( not(thread1.done() and thread2.done())):
			time.sleep(1)

	except KeyboardInterrupt:
		print('exit')
		wait1ms(100)
		bus.shutdown()
		wait1ms(100)


if __name__ == "__main__":
	try:
		main()
	except:
		QUIT_REQUEST = 1


