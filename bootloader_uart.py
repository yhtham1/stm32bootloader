#! /usr/bin/python3
# -*- coding: utf-8 -*-
# ＵＴＦ８
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

"""
	disp_SourceLine( 'ERR', sys._getframe())
"""


def disp_SourceLine(msg, a):
	name = a.f_code.co_name
	line = a.f_code.co_firstlineno
	fn = os.path.basename(a.f_code.co_filename)
	print('{} {}()@{} Line:{}'.format(msg, name, fn, line))


def wait1ms(n):
	time.sleep(n * 1e-3)


def make_address(add):
	ans = bytearray()
	a1 = (add >> 24) & 0xff
	a2 = (add >> 16) & 0xff
	a3 = (add >> 8) & 0xff
	a4 = (add) & 0xff
	ans.append(a1)
	ans.append(a2)
	ans.append(a3)
	ans.append(a4)
	return ans


def append_checksum(c):
	ans = 0
	for i in range(len(c)):
		ans ^= c[i]
	#		print(i,'{:02X}'.format(ans))
	c.append(ans)
	return c


class stm32bootloader(serial.Serial):
	ACK = b'\x79'
	NAK = b'\x1f'
	# ERASE_CMD = 0x44
	CMD_LIST = []
	CMD_TTL = (
		'Bootloader Version',
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

	def __init__(self, port):
		try:
			super().__init__(port=port, baudrate=115200, timeout=1, parity=serial.PARITY_NONE)
		except serial.SerialException:
			print('COM PORT ERROR[{}]'.format(port))
		self.mode = 0

	def showPort(self):
		print('COMPORT:{}'.format(self.port))

	def siowrite(self, b):
		self.write(b)

	def send(self, utfmsg):
		self.set_normalmode()
		a = utfmsg + '\r'
		bmsg = a.encode('utf-8')
		self.siowrite(bmsg)

	def query(self, msg):
		"""
		:param msg: utf8で問い合わせる。
		:return:
		"""
		self.timeout = 0.5
		self.send(msg)
		bline = self.readline()
		if bline is None:
			return ''
		ans1 = bline.decode('utf8')
		ans = ans1.strip('\r\n')
		return ans

	def disp_serial(self):
		print('COMPORT:{} BAUD:{} parity:{}'.format(
			self.port, self.baudrate, self.parity)
		)

	def setParityNone(self):
		if self.isOpen():
			self.close()
		self.parity = serial.PARITY_NONE
		self.open()
		print('setParityNone:', end='')
		self.disp_serial()

	def setParityEven(self):
		if self.is_open:
			self.close()
		self.parity = serial.PARITY_EVEN
		self.open()
		self.disp_serial()

	####################################################################
	def clear_rxq(self, t=0.02):
		self.timeout = t
		ct = 0
		while True:
			c = self.read()
			if 0 == len(c):
				time.sleep(0.002)
				# print(' OK',end='')
				break
			else:
				time.sleep(0.02)
			ct += 1
		return ct

	####################################################################
	def wait_ack(self):
		self.timeout = 0.01
		ct = 0
		st = time.time()
		while True:
			c = self.read()
			if 1 == len(c):
				self.timeout = 0.5
				print('')
				return c
			print('\rwait_ack {:5.1f} sec'.format(time.time() - st), end='')
			ct += 1

	####################################################################
	def getIDN(self):
		self.siowrite('*IDN?\r\n'.encode('utf-8'))
		b_ans = self.read(250)
		k_ans = b_ans.decode('utf-8')
		ans = k_ans.strip('\r\n')
		return ans

	def cmdGet(self, display=True):
		"""
		CMD_LISTを生成する。
		:param display:リストを画面表示する
		:return:
		"""
		self.CMD_LIST = []
		cmd = 0x00
		self.clear_rxq()
		ans = []
		self.siowrite(bytearray([cmd, 0xff ^ cmd]))
		c = self.read()
		if c == self.NAK:
			print('ERR1a {:02X}'.format(c[0]))
			return c[0]
		if c == self.ACK:
			c = self.read()
			n = c[0]
			# print('--------------- cmdGet() -------------')

			for i in range(n + 1):
				c = self.read()
				# print('{:2} {:>30} : 0x{:02X}'.format(i, CMD_TTL[i], c[0]))
				self.CMD_LIST.append(c[0])
				ans.append(c[0])
			c = self.read()
		else:
			return None
		if True == display:
			print('--------------------------------------')
			for i in range(len(ans)):
				print("{:>30} : 0x{:02X}".format(self.CMD_TTL[i], ans[i]))
			print('--------------------------------------')
		return ans

	####################################################################
	def cmdGetID(self):
		self.timeout = 0.1
		self.clear_rxq()
		cmd = self.CMD_LIST[3]
		self.siowrite(bytearray([cmd, 0xff ^ cmd]))
		c = self.read()
		if c != self.ACK:
			print('cmdGetID():ERR1')
			return -1  # error
		if c == self.ACK:
			c = self.read()
			n = c[0]
			print('bytes {}'.format(n))
			c = self.read(n + 1)
			print('Device ID:{:02X}{:02X}'.format(c[0], c[1]))
			c = self.read()
			if c == self.ACK:
				pass
			else:
				print('ERR3')
				return -1  # error
		else:
			print('ERR2')
			return -1  # error
		return 0  # OK

	####################################################################
	def cmdReadMemory(self, add, length):
		self.timeout = 0.1
		cmd = self.CMD_LIST[4]
		self.siowrite(bytearray([cmd, 0xff ^ cmd]))
		c = self.read()
		if c != self.ACK:
			print('cmdReadMemory():{:02X} ERR1', c[0])
			return None  # error
		self.siowrite(append_checksum(make_address(add)))
		c = self.read()
		if c != self.ACK:
			print('cmdReadMemory():{:02X} ERR2', c[0])
			return None  # error
		len1 = length - 1
		self.siowrite(bytearray([len1, 0xff ^ len1]))
		c = self.read()
		if c != self.ACK:
			print('cmdReadMemory():{:02X} ERR3', c[0])
			return None  # error
		ans = bytearray(b'')
		for i in range(length):
			c = self.read()
			ans.append(c[0])
		return ans

	####################################################################
	def cmdGo(self, add):
		self.timeout = 0.1
		self.clear_rxq()
		cmd = self.CMD_LIST[5]
		self.siowrite(bytearray([cmd, 0xff ^ cmd]))
		c = self.read()
		if c != self.ACK:
			print('cmdGo():{:02X} ERR1', c[0])
			return -1  # error
		self.siowrite(append_checksum(make_address(add)))
		c = self.read()
		if c != self.ACK:
			print('cmdGo():{:02X} ERR2', c[0])
			return -1  # error
		print('cmdGo(0x{:08X}):OK'.format(add))
		return 0  # OK

	####################################################################
	def cmdWriteMemory(self, add, dat):
		self.timeout = 0.1
		cmd = self.CMD_LIST[6]
		self.siowrite(bytearray([cmd, 0xff ^ cmd]))
		length = len(dat)
		c = self.read()
		if c != self.ACK:
			print('cmdWriteMemory():0x{:02X} ERR1'.format(c[0]))
			return -1  # error
		self.siowrite(append_checksum(make_address(add)))
		c = self.read()
		if c != self.ACK:
			print('cmdWriteMemory():0x{:02X} ERR2'.format(c[0]))
			return -1  # error
		len1 = length - 1
		dat2 = bytearray([len1])
		dat2 += dat
		dat3 = append_checksum(dat2)
		self.siowrite(dat3)
		c = self.read()
		if c != self.ACK:
			print('cmdWriteMemory():0x{:02X} ERR3'.format(c[0]))
			return -1  # error
		return 0  # OK

	####################################################################
	def cmdErase(self):
		self.set_loadermode()
		self.timeout = 0.1
		cmd = self.CMD_LIST[7]
		print('ERASECMD:{:02X}'.format(cmd))
		self.siowrite(bytearray([cmd, 0xff ^ cmd]))
		c = self.read()
		if c != self.ACK:
			print('cmdErase():0x{:02X} ERR1'.format(c[0]))
			return
		print('消去開始 最大16秒程度')
		if 0x43 == cmd:  # Erase Memory Command
			dat2 = bytearray([0xff])
			dat3 = append_checksum(dat2)
		else:  # Extended Erase Memory command
			dat2 = bytearray([0xff, 0xff])
			dat3 = append_checksum(dat2)
		print(dat3)
		self.siowrite(dat3)
		c = self.wait_ack()
		if c != self.ACK:
			print('cmdErase():0x{:02X} ERR2'.format(c[0]))
			return
		return

	####################################################################
	def ReadMemory_sub(self, add, length, tick_char):
		self.clear_rxq()
		ct = 0
		add1 = add
		num1 = length
		ans = bytearray(b'')
		while 256 < num1:
			sz = 256
			# print(tick_char, end='')
			sys.stdout.flush()
			bk = self.cmdReadMemory(add1, sz)
			ans += bk
			add1 += sz
			num1 -= sz
			ct += sz
			print('{:8}/{} {:5.1f}%\r'.format(ct, length, 100.0 * ct / length), end='')
		if len(tick_char):
			ct += num1
			print('{:8}/{} {:5.1f}%\r'.format(ct, length, 100.0 * ct / length), end='')
			# print('{:8}/{}\r'.format(ct,length),end='')
			print('')
		if num1 <= 0:
			return ans
		bk = self.cmdReadMemory(add1, num1)
		ans += bk
		return ans

	def ReadMemory(self, add, length):
		self.set_loadermode()
		return self.ReadMemory_sub(add, length, '*')

	def ReadMemoryQuiet(self, add, length):
		self.set_loadermode()
		return self.ReadMemory_sub(add, length, '')

	def WriteMemory(self, baseadd, dat):
		self.set_loadermode()
		self.clear_rxq()
		self.timeout = 0.1
		length = len(dat)
		add1 = 0
		num1 = length
		bk = bytearray(256)
		while 256 < num1:
			sz = 256
			for i in range(sz):
				bk[i] = dat[i + add1]
			#		print('*', end='')
			print('--------------------------- {:08X}'.format(baseadd + add1))
			dump(baseadd + add1, bk)
			self.cmdWriteMemory(baseadd + add1, bk)
			add1 += sz
			num1 -= sz
		if 0 < num1:
			bk1 = bytearray(num1)
			for i in range(num1):
				bk1[i] = dat[add1 + i]
			print('\r--------------------------- {:08X}'.format(baseadd + add1))
			dump(baseadd + add1, bk1)
			self.cmdWriteMemory(baseadd + add1, bk1)
		print('')
		return

	######################## 0x7fを送ってNAKが返るまで繰り返す
	def sync(self, retry_ct=30):
		if 2 != self.mode:
			return -1  # error
		self.clear_rxq(0.1)
		self.timeout = 0.1
		# print('------------ SYNC START ---------')
		ct = 0
		while True:
			# print(ct)
			self.siowrite(bytearray([0x7f]))
			time.sleep(0.001)
			c = self.read()
			if 1 == len(c):
				if self.NAK == c:
					# print('------------ SYNC OK ------------')
					return 0  # no error
			ct += 1
			if retry_ct < ct:
				print('sync error')
				return -1  # error

	def ProgramStart(self):
		self.set_loadermode()
		jmp = self.ReadMemoryQuiet(0x08000004, 4)
		dump(0x08000004, jmp)
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
		self.cmdGo(add)

	def disp0x10(self, add):
		self.set_loadermode()
		buf = self.ReadMemoryQuiet(add, 0x10)
		dump(add, buf)

	def BootDump(self):
		self.set_loadermode()
		add = 0x08000000
		len1 = 0x800
		b = self.ReadMemoryQuiet(add, len1)
		dump(add, b)

	def init(self):  # 0: OK -1:NG
		self.mode = 0
		if not self.is_open:
			try:
				self.open()
			except serial.SerialException:
				return -1  # ERROR
		self.clear_rxq()
		return 0

	def set_normalmode(self):
		if 1 == self.mode:
			return 0
		print('set_normalmode')
		self.init()
		self.setParityNone()
		self.clear_rxq(0.1)
		self.mode = 1

	def set_loadermode(self):
		if 2 == self.mode:
			return 0  # no error
		self.init()
		self.mode = 2
		self.setParityEven()
		self.clear_rxq(0.1)
		if 0 != self.sync():
			return -1  # error
		ans = self.cmdGet(False)
		print('READY uart_bootloader.init()')
		return 0  # no error

	def FlashDump(self):
		if self.set_loadermode() < 0:
			return -1  # error
		self.disp0x10(0x08000000)
		self.disp0x10(0x08004000)
		self.disp0x10(0x08008000)
		self.disp0x10(0x0800c000)
		self.disp0x10(0x08010000)
		return 0  # no error


def getFirmDate(txt1):
	ct = txt1.split(',')
	if 4 == len(ct):
		if 0 == ct[3].find('VER'):
			version = ct[3]
			dat1 = int(version[3:version.find(' ')].strip())
			print('firmware date:{}'.format(dat1))
			return dat1
	return -1


def main():
	i = 1
	port = 'com1'
	while i < len(sys.argv):  # in range(1, len(sys.argv)):
		arg2 = sys.argv[i].strip()
		if 0 <= arg2.find('--port'):
			port = sys.argv[i + 1].strip()
			i += 2
			continue
		# normal 処理
		i += 1
	# ---------------------------------------------------------------
	bl = stm32bootloader(port)
	bl.close()
	if bl.init() < 0:
		return 1  # error
	bl.set_normalmode()
	bl.clear_rxq(0.1)
	bl.send('')
	time.sleep(0.2)
	bl.disp_serial()
	ans = bl.query('*idn?')
	while 0 <= ans.find('error'):
		print(ans)
		bl.clear_rxq(0.1)
		ans = bl.query('*idn?')
	if 0 <= ans.find('THAMWAY'):
		print('*idn?:{}'.format(ans))
		date1 = getFirmDate(ans)
		print(date1)
		if date1 < 20210201:
			bl.send('reboot:1')  # reboot bug version
		else:
			bl.send('reboot:2')
		time.sleep(3)
	if bl.FlashDump() < 0:
		return -1
	time.sleep(1)
	bl.close()
	return 0  # no error


# ----------------------------------------------------------
if __name__ == '__main__':
	ans = main()
	sys.exit(ans)
