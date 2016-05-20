#!/usr/bin/python

from rflib import *
import sys
import bitstring
from pyfiglet import Figlet

f = Figlet(font='doh')

def manchester_decode(symbols):
    bits = []
    for dibit in symbols.cut(2):
        if dibit == '0b01':
            bits.append(0)
        elif dibit == '0b10':
            bits.append(1)
        else:
#            print "invalid manchester encoding"
            raise ValueError
    return bitstring.BitStream(bits)

def siemens_ook80_validate(bits, checksum):
    # include bits from sync word
    padded_bits = '0b0100' + bits
    total = 0
    for word in padded_bits.cut(8, 0, padded_bits.len-8):
        total += word.int & 0xff
    if checksum != total & 0xff:
#        print "invalid checksum"
        raise ValueError

# Siemens VDO TPMS 80 bit OOK format
def siemens_ook80_decode(pkt):
    try:
        data = manchester_decode(bitstring.pack('bytes', pkt)[:152])
#        print data.bin
#        print "ffffffffffffffffffffiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiippppppppttttttttcccccccc"
        function, identifier, pressure, temperature, checksum = data.unpack('uint:20, uint:32, uint:8, uint:8, uint:8')
#        print "function code: %05x" % function
#        print "ID: %08x" % identifier
#        print "pressure: %02x" % pressure
#        print "temperature: %02x" % temperature
#        print "checksum: %02x" % checksum
        siemens_ook80_validate(data, checksum)
    except:
        return
#    print "checksum valid"
    pressure = pressure  * 4 / 3
    print f.renderText("%02d" % pressure)

def rxook(device):
    device.setFreq(315000000)
    device.setMdmModulation(MOD_ASK_OOK)
    device.setMdmDRate(8400)
    device.setPktPQT(7)
    device.setMdmSyncMode(SYNC_MODE_16_16)
    device.setMdmSyncWord(0b0101010101100101)
    device.makePktFLEN(20)

    while not keystop():
        try:
            pkt, ts = device.RFrecv()
#            print "Received:  %s" % pkt.encode('hex')
            siemens_ook80_decode(pkt)
        except ChipconUsbTimeoutException:
            pass
    sys.stdin.read(1)

if __name__ == "__main__":
	device = RfCat()
	rxook(device)
