#!/usr/bin/python
#
# usage from rfcat interactive shell:
#   %run sl.py
#   rxtpms(d)

from rflib import *
from itertools import izip
import sys

def print_packet(payload):
	address = payload[1] << 24 | payload[2] << 16 | payload[3] << 8 | payload[4]
	pressure = payload[6] * 4 / 3
	temperature = payload[7] - 50
	print "Address: %08x, Pressure: %d kPa, Temp: %d C" % (address, pressure, temperature)

def crc_80(payload):
	polynomial = 0x01
	value = 0
	for byte in payload[1:]:
		for i in range(8):
			bit1 = (byte >> i) & 0x01
			bit2 = value & 0x01
			value = value >> 1
			value = value | (bit1^bit2) << 7
	return value

def packet_valid(payload):
	if crc_80(payload[:-1]) == payload[-1]:
		return True
	return False

def grouped(iterable, n):
    "s -> (s0,s1,s2,...sn-1), (sn,sn+1,sn+2,...s2n-1), (s2n,s2n+1,s2n+2,...s3n-1), ..."
    return izip(*[iter(iterable)]*n)

def decode_manchester_byte(x, y):
	z = (x & 0x80) | (x & 0x20) << 1 | (x & 0x08) << 2 | (x & 0x02) << 3 \
	    | (y & 0x80) >> 4 | (y & 0x20) >> 3 | (y & 0x08) >> 2 | (y & 0x02) >> 1
	#print "%02x" % z
	return z

def decode_manchester(pkt):
	return [
		decode_manchester_byte(x, y)
		for x, y in grouped(pkt, 2)
		]

def config_radio(device):
#	device.setFreq(433000000)
#	device.setFreq(315009000)
	device.setFreq(315000000)
	device.setMdmModulation(MOD_2FSK)
#	device.setEnableMdmManchester()
	device.setMdmDRate(19200)
#	device.setMdmSyncMode(2)
	device.setMdmSyncMode(SYNCM_16_of_16)
	device.setMdmSyncWord(0x5556)
	device.setMdmNumPreamble(0)
	device.setMaxPower()
	device.makePktFLEN(20)

def rxtpms(device):
	config_radio(device)
	while not keystop():
		try:
			pkt, ts = device.RFrecv()
			#print "Received:  %s" % pkt.encode('hex')
			packet = [ord(p) for p in pkt]
			payload = decode_manchester(packet)
			#print "Decoded:  ",  ["%02x" % p for p in payload]
			if packet_valid(payload):
				print "Decoded:  ",  ' '.join(["%02x" % p for p in payload])
				print_packet(payload)
		except ChipconUsbTimeoutException:
			pass
	sys.stdin.read(1)

if __name__ == "__main__":
	device = RfCat()
	rxtpms(device)
	
