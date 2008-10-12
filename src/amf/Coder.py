
from AMFDecoder import AMFDecoder
from AMFEncoder import AMFEncoder
from AMFXML import ToXML, FromXML

class SimpleAMFCoder:
	@classmethod
	def encode(cls, xml):
		fromxml = FromXML(xml)
		packet = fromxml.get_packet()
		encoder = AMFEncoder(xml)
		return encoder.encode()
	@classmethod
	def decode(cls, raw):
		decoder = AMFDecoder(raw)
		packet = decoder.decode()
		toxml = ToXML(packet)
		return toxml.get_xml()

