
from AMFDecoder import AMFDecoder
from AMFEncoder import AMFEncoder
from AMFXML import ToXML, FromXML

class SimpleAMFCoder:
	@classmethod
	def encode(cls, xml):
		#TODO: give messageId an uniq uuid
		#import uuid
		#messageId = str(uuid.uuid1())
		#import re
		#xml = re.sub(r'"messageId">[^<>]+</member>', r'"messageId">'+messageId+r'</member>', xml)

		fromxml = FromXML(xml)
		packet = fromxml.get_packet()
		encoder = AMFEncoder(packet)
		return encoder.encode()
	@classmethod
	def decode(cls, raw):
		decoder = AMFDecoder(raw)
		packet = decoder.decode()
		toxml = ToXML(packet)
		return toxml.get_xml()

