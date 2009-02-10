
__all__ = ['register_alias', 'find_alias']

from AMFTypes import *

ALIAS_MAP = {}

def register_alias(alias, ext_type):
	ALIAS_MAP[alias] = ext_type

def register_alias_for(ext_type):
	register_alias(ext_type.CLASS_ALIAS, ext_type)

def register_predefined_aliases():
	register_alias('flex.messaging.io.ArrayCollection', DefaultExtObject)
	#register_alias('DSA', BlazeDSAsyncMessage)
	register_alias('DSC', BlazeDSCommandMessage)
	register_alias('DSK', BlazeDSAcknowledgeMessage)

def find_alias(alias):
	return ALIAS_MAP[alias]


class DefaultExtObject(ExtObject):
	def __init__(self, trait):
		ExtObject.__init__(self, trait)
		self.value = None

	def decode(self, decoder):
		self.value = decoder.read_value()

	def encode(self, encoder):
		encoder.write_value(self.value)

	def __str__(self):
		trait = self.trait.get_referenced()
		assert trait.__class__ == TraitExt
		return "ext-object<{%s}>=(%s)" % (trait, self.value)

	def __repr__(self):
		return str(self)


HAS_NEXT_FLAG = 128
BODY_FLAG = 1
CLIENT_ID_FLAG = 2
DESTINATION_FLAG = 4
HEADERS_FLAG = 8
MESSAGE_ID_FLAG = 16
TIMESTAMP_FLAG = 32
TIME_TO_LIVE_FLAG = 64

CLIENT_ID_BYTES_FLAG = 1
MESSAGE_ID_BYTES_FLAG = 2

CORRELATION_ID_FLAG = 1
CORRELATION_ID_BYTES_FLAG = 2



class BlazeDSAbstractMessage(ExtObject):
	def __init__(self, trait):
		ExtObject.__init__(self, trait)

		self.flag1 = 0
		self.flag2 = 0

		self.body = None
		self.clientId = None
		self.destination = None
		self.headers = None
		self.messageId = None
		self.timestamp = None
		self.timeToLive = None

		self.clientId = None
		self.messageId = None

		self.flag3 = 0

		self.correlationId = None
		self.correlationIdBytes = None

	def decode(self, decoder):
		self.flag1 = decoder.read_byte()

		if self.flag1 & HAS_NEXT_FLAG:
			self.flag2 = decoder.read_byte()
			assert (self.flag2 & HAS_NEXT_FLAG) == 0, "You have more flags to read, implement code here!"
		else:
			self.flags2 = 0

		if (self.flag1 & BODY_FLAG) != 0:
			self.body = decoder.read_value()

		if (self.flag1 & CLIENT_ID_FLAG) != 0:
			self.clientId = decoder.read_value()

		if (self.flag1 & DESTINATION_FLAG) != 0:
			self.destination = decoder.read_value()

		if (self.flag1 & HEADERS_FLAG) != 0:
			self.headers = decoder.read_value()

		if (self.flag1 & MESSAGE_ID_FLAG) != 0:
			self.messageId = decoder.read_value()

		if (self.flag1 & TIMESTAMP_FLAG) != 0:
			self.timestamp = decoder.read_value()

		if (self.flag1 & TIME_TO_LIVE_FLAG) != 0:
			self.timeToLive = decoder.read_value()

		if (self.flag2 & CLIENT_ID_BYTES_FLAG) != 0:
			self.clientId = decoder.read_value()

		if (self.flag2 & MESSAGE_ID_BYTES_FLAG) != 0:
			self.messageId = decoder.read_value()

		self.flag3 = decoder.read_byte()

		if (self.flag3 & CORRELATION_ID_FLAG) != 0:
			self.correlationId = decoder.read_value()

		if (self.flag3 & CORRELATION_ID_BYTES_FLAG) != 0:
			self.correlationIdBytes = decoder.read_value()

	def encode(self, encoder):
		encoder.write_byte(self.flag1)
		encoder.write_byte(self.flag2)

		if (self.flag1 & BODY_FLAG) != 0:
			encoder.write_value(self.body)

		if (self.flag1 & CLIENT_ID_FLAG) != 0:
			encoder.write_value(self.clientId)

		if (self.flag1 & DESTINATION_FLAG) != 0:
			encoder.write_value(self.destination)

		if (self.flag1 & HEADERS_FLAG) != 0:
			encoder.write_value(self.headers)

		if (self.flag1 & MESSAGE_ID_FLAG) != 0:
			encoder.write_value(self.messageId)

		if (self.flag1 & TIMESTAMP_FLAG) != 0:
			encoder.write_value(self.timestamp)

		if (self.flag1 & TIME_TO_LIVE_FLAG) != 0:
			encoder.write_value(self.timeToLive)


		if (self.flag2 & CLIENT_ID_BYTES_FLAG) != 0:
			encoder.write_value(self.clientId)

		if (self.flag2 & MESSAGE_ID_BYTES_FLAG) != 0:
			encoder.write_value(self.messageId)


		encoder.write_byte(self.flag3)

		if (self.flag3 & CORRELATION_ID_FLAG) != 0:
			encoder.write_value(self.correlationId)

		if (self.flag3 & CORRELATION_ID_BYTES_FLAG) != 0:
			encoder.write_value(self.correlationIdBytes)


class BlazeDSAsyncMessage(BlazeDSAbstractMessage):
	CLASS_ALIAS = 'DSA'

	def __init__(self, trait):
		BlazeDSAbstractMessage.__init__(self, trait)

	def decode(self, decoder):
		BlazeDSAbstractMessage.decode(self, decoder)

	def encode(self, encoder):
		BlazeDSAbstractMessage.encode(self, encoder)

	def __str__(self):
		trait = self.trait.get_referenced()
		assert trait.__class__ == TraitExt

		exp = '''body: %s
clientId: %s
destination: %s
headers: %s
messageId: %s
timestamp: %s
timeToLive: %s
clientId: %s
messageId: %s
correlationId: %s
correlationIdBytes: %s
''' % (self.body,
                    self.clientId,
                    self.destination,
                    self.headers,
                    self.messageId,
                    self.timestamp,
                    self.timeToLive,
                    self.clientId,
                    self.messageId,
                    self.correlationId,
                    self.correlationIdBytes,
                    )

		return "ext-object<{%s}>=(%s)" % (trait, exp)

	def __repr__(self):
		return str(self)


class BlazeDSAcknowledgeMessage(BlazeDSAbstractMessage):
	CLASS_ALIAS = 'DSK'

	def __init__(self, trait):
		BlazeDSAbstractMessage.__init__(self, trait)

	def decode(self, decoder):
		BlazeDSAbstractMessage.decode(self, decoder)
		flag = decoder.read_byte()
		assert flag == 0, 'flag should be 0, but %d' % flag

	def encode(self, encoder):
		BlazeDSAbstractMessage.encode(self, encoder)
		flag = 0
		encoder.write_byte(flag)

	def __str__(self):
		trait = self.trait.get_referenced()
		assert trait.__class__ == TraitExt

		exp = '''body: %s
clientId: %s
destination: %s
headers: %s
messageId: %s
timestamp: %s
timeToLive: %s
clientId: %s
messageId: %s
correlationId: %s
correlationIdBytes: %s
''' % (self.body,
                    self.clientId,
                    self.destination,
                    self.headers,
                    self.messageId,
                    self.timestamp,
                    self.timeToLive,
                    self.clientId,
                    self.messageId,
                    self.correlationId,
                    self.correlationIdBytes,
                    )

		return "ext-object<{%s}>=(%s)" % (trait, exp)

	def __repr__(self):
		return str(self)


OPERATION_FLAG = 1
class BlazeDSCommandMessage(BlazeDSAbstractMessage):
	CLASS_ALIAS = 'DSC'

	def __init__(self, trait):
		BlazeDSAbstractMessage.__init__(self, trait)

		self.operation = None

	def decode(self, decoder):
		BlazeDSAbstractMessage.decode(self, decoder)
		flag = decoder.read_byte()
		assert flag == 1
		if flag & OPERATION_FLAG:
			self.operation = decoder.read_value()

	def encode(self, encoder):
		BlazeDSAbstractMessage.encode(self, encoder)

		assert self.operation is not None

		flag = 0
		if self.operation is not None:
			flag |= OPERATION_FLAG
			encoder.write_byte(flag)
			encoder.write_value(self.operation)
		else:
			encoder.write_byte(flag)

	def __str__(self):
		trait = self.trait.get_referenced()
		assert trait.__class__ == TraitExt

		exp = '''body: %s
clientId: %s
destination: %s
headers: %s
messageId: %s
timestamp: %s
timeToLive: %s
clientId: %s
messageId: %s
correlationId: %s
correlationIdBytes: %s
operation: %s
''' % (self.body,
                    self.clientId,
                    self.destination,
                    self.headers,
                    self.messageId,
                    self.timestamp,
                    self.timeToLive,
                    self.clientId,
                    self.messageId,
                    self.correlationId,
                    self.correlationIdBytes,
                    self.operation,
                    )

		return "ext-object<{%s}>=(%s)" % (trait, exp)

	def __repr__(self):
		return str(self)



register_predefined_aliases()


