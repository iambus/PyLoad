
from AMFDecoder import AMFDecoder
from AMFEncoder import AMFEncoder
from AMFXML2 import ToXML, FromXML

from uuid import uuid1
def new_uuid(x):
	return r'"messageId">%s</member>' % uuid1()

class SimpleAMFCoder:
	@classmethod
	def encode(cls, xml):
		#TODO: give messageId an uniq uuid
		#import uuid
		#messageId = str(uuid.uuid1())
		#import re
		#xml = re.sub(r'"messageId">[^<>]+</member>', r'"messageId">'+messageId+r'</member>', xml)
		#import re
		#xml = re.sub(r'"messageId">[^<>]+</member>', new_uuid, xml)

		fromxml = FromXML(xml)
		packet = fromxml.get_packet()
		encoder = AMFEncoder(packet)
		return encoder.encode()
	@classmethod
	def decode(cls, raw):
		try:
			decoder = AMFDecoder(raw)
			packet = decoder.decode()
			toxml = ToXML(packet)
			return toxml.get_xml()
		except:
			import datetime
			filename = datetime.datetime.now().strftime('can-not-be-decoded-amf-%Y-%m-%d-%H-%M-%S.txt')
			fp = open(filename, 'wb')
			fp.write(raw)
			fp.close()
			raise

