#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from inputimeout import inputimeout, TimeoutOccurred

####################################################################
def main():
	try:
		something = inputimeout(prompt='>>', timeout=5)
	except TimeoutOccurred:
		something = 'something'
	print(something)

if __name__ == "__main__":
	main()


