
import unittest

from AMFDecoder import AMFDecoder
from AMFEncoder import AMFEncoder

##################################################

def bits2int(bits):
	bits = bits.replace(' ', '')
	v = 0
	for i in bits:
		assert i == '0' or i == '1'
		v = (v << 1) | int(i)
	return v
def bits2str(bits):
	i = bits2int(bits)
	v = ''
	while i > 0:
		v = chr(i&0xff) + v
		i >>= 8
	v = v or '\x00'
	return v

def int2bits(i):
	assert i >= 0
	v = ''
	while i > 0:
		v = str(i&1) + v
		i >>= 1
	v = v or '0'
	return v

##################################################

class TestBits(unittest.TestCase):
	def testBits2Str(self):
		self.assertEquals(bits2str('0'), '\x00')
		self.assertEquals(bits2str('1'), '\x01')
		self.assertEquals(bits2str('1111'), '\x0f')
		self.assertEquals(bits2str('1111 1111'), '\xff')
		self.assertEquals(bits2str('0000 0000'), '\x00')
		self.assertEquals(bits2str('0011 0101'), '\x35')

	def testBits2Int(self):
		self.assertEquals(bits2int('0'), 0)
		self.assertEquals(bits2int('1'), 1)
		self.assertEquals(bits2int('10'), 2)
		self.assertEquals(bits2int('101111'), 0x2f)
		self.assertEquals(bits2int('0011100'), 0x10+12)

	def testInt2Bits(self):
		self.assertEquals(int2bits(0), '0')
		self.assertEquals(int2bits(1), '1')
		self.assertEquals(int2bits(2), '10')
		self.assertEquals(int2bits(0x2f), '101111')
		self.assertEquals(int2bits(0x10+12), '11100')

##################################################

class TestPrimitive(unittest.TestCase):
	def setUp(self):
		pass

	def assertU29Decode(self, s, i):
		self.assertEquals(AMFDecoder(bits2str(s)).read_u29(), i)

	def assertU29Encode(self, i, bits):
		bits = bits.replace(' ', '')
		bits = bits.lstrip('0')
		import StringIO
		output = StringIO.StringIO()
		encoder = AMFEncoder(None, output)
		encoder.write_u29(i)
		self.assertEquals(output.getvalue(), bits2str(bits))
		output.close()

	def testU29(self):
		#0011 0101 = 53
		#1000 0001 0101 0100 = 212
		#1000 0110 1100 1010 0011 1111 = 107839
		#1111 1111 1111 1111 1111 1111 1111 1111 = -1
		#XXX: are they correct?
		#1100 0001 1111 1111 1111 1111 1111 1111 = -268435456
		#1100 0000 1000 0001 1000 0001 1000 0000 = 268435455

		self.assertU29Decode(('0011 0101'), 53)
		self.assertU29Decode(('1000 0001 0101 0100'), 212)
		self.assertU29Decode(('1000 0110 1100 1010 0011 1111'), 107839)
		self.assertU29Decode(('1111 1111 1111 1111 1111 1111 1111 1111'), -1)
#		self.assertU29Decode(('1100 0001 1111 1111 1111 1111 1111 1111'), -268435456)
#		self.assertU29Decode(('1100 0000 1000 0001 1000 0001 1000 0000'), 268435455)

		self.assertU29Encode(53, '0011 0101')
		self.assertU29Encode(212, '1000 0001 0101 0100')
		self.assertU29Encode(107839, '1000 0110 1100 1010 0011 1111')
		self.assertU29Encode(-1, '1111 1111 1111 1111 1111 1111 1111 1111')
#		self.assertU29Encode(-268435456, '1100 0001 1111 1111 1111 1111 1111 1111')
#		self.assertU29Encode(268435455, '1100 0000 1000 0001 1000 0001 1000 0000')

print hex(bits2int('00011111 11100000 00000000 00000000'))

if __name__ == '__main__':
	unittest.main()

