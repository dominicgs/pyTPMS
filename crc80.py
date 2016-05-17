#!/usr/bin/env python

def print_hex_list(lst):
	print ' '.join(["%02x" % item for item in lst])

def crc_80(payload):
	print_hex_list(payload)
	polynomial = 0x01
	value = 0
	for byte in payload[1:]:
		for i in range(8):
			bit1 = (byte >> i) & 0x01
			bit2 = value & 0x01
			value = value >> 1
			value = value | (bit1^bit2) << 7
	return value

if __name__ == '__main__':
	payload = [0xc0, 0x0c, 0xbc, 0xfe, 0xee, 0x02, 0x01, 0x4a, 0x0d, 0xe4]
	crc = crc_80(payload[:-1])
	print "%02x %02x" % (crc, payload[-1])

