#!/usr/bin/python

from rflib import *
import sys
import bitstring

def manchester_decode(symbols):
    bits = []
    for dibit in symbols.cut(2):
        if dibit == '0b01':
            bits.append(0)
        elif dibit == '0b10':
            bits.append(1)
        else:
            print "invalid manchester encoding"
            raise ValueError
    return bitstring.BitStream(bits)

def schrader_ook37_validate(bits, checksum):
    padded_bits = '0b0' + bits
    total = 0
    for word in padded_bits.cut(2, 0, padded_bits.len-2):
        total += word.int & 3
    if checksum != 3 - (total & 3):
        print "invalid checksum"
        raise ValueError

# Schrader TPMS 37 bit OOK format
def schrader_ook37_decode(pkt):
    try:
        data = manchester_decode(bitstring.pack('bytes', pkt)[:74])
        print data.bin
        print "fffiiiiiiiiiiiiiiiiiiiiiiiippppppppcc"
        function, identifier, pressure, checksum = data.unpack('uint:3, uint:24, uint:8, uint:2')
        print "function code: %01x" % function
        print "ID: %06x" % identifier
        print "pressure: %02x" % pressure
        print "checksum: %01x" % checksum
        schrader_ook37_validate(data, checksum)
    except:
        return
    print "checksum valid"

def rxook(device):
    device.setFreq(315052000)
    device.setMdmModulation(MOD_ASK_OOK)
    device.setMdmDRate(8192)
    device.setPktPQT(4)
    device.setMdmSyncMode(SYNC_MODE_16_16)
    device.setMdmSyncWord(0b0101010101011110)
    device.makePktFLEN(10)

    while not keystop():
        try:
            pkt, ts = device.RFrecv()
            print "Received:  %s" % pkt.encode('hex')
            schrader_ook37_decode(pkt)
        except ChipconUsbTimeoutException:
            pass
    sys.stdin.read(1)

if __name__ == "__main__":
	device = RfCat()
	rxook(device)