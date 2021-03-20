#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#ＵＴＦ８

import time
from  concurrent.futures import ThreadPoolExecutor

QUIT_REQUEST = 0
ct = 0

def func1():
	while 0==QUIT_REQUEST:
		print('func1():{} QUIT_REQUEST:{}'.format(ct, QUIT_REQUEST))
		time.sleep(1)

def func2():
	while 0==QUIT_REQUEST:
		print('func2():{} QUIT_REQUEST:{}'.format(ct, QUIT_REQUEST))
		time.sleep(1)
def func_QUIT_REQUEST():
	global QUIT_REQUEST
	print('func_QUIT_REQUEST()')
	QUIT_REQUEST = 1
	while True:
		pass
def main():
	global ct
	EXECUTOR = ThreadPoolExecutor(max_workers=4)
	thread1 = EXECUTOR.submit(func1)
	thread2 = EXECUTOR.submit(func2)
	while( not(thread1.done() and thread2.done())):
		ct += 1
		time.sleep(1)
	return
if __name__ == "__main__":
	try:
		main()
	except:
		QUIT_REQUEST = 1


