
from AMFExtAlias import find_alias

XMLER_MAP = {}

def register_ext_xmler(alias, xmler):
	XMLER_MAP[alias] = xmler

def register_predefined_ext_xmlers():
	register_ext_xmler('flex.messaging.io.ArrayCollection', DefaultXMLer())
	#register_ext_xmler('DSA', BlazeDSAsyncMessageXMLer())
	register_ext_xmler('DSC', BlazeDSCommandMessageXMLer())
	register_ext_xmler('DSK', BlazeDSAcknowledgeMessageXMLer())

def find_xmler(obj):
	return XMLER_MAP[obj]


class DefaultXMLer:
	def to_xml(self, to_xml_er, obj, node):
		to_xml_er.create_value_node(node, obj.value)

	def from_xml(self, from_xml_er, obj, value_node):
		obj.value = from_xml_er.get_value(value_node)

class BlazeDSAbstractMessageXMLer:
	def __init__(self):
		pass

	def to_xml(self, to_xml_er, obj, parent):
		node = to_xml_er.create_child(parent, obj.CLASS_ALIAS)

		self.create_node(to_xml_er, node, obj.flag1, 'flag1')
		self.create_node(to_xml_er, node, obj.flag2, 'flag2')

		self.create_node(to_xml_er, node, obj.body, 'body')
		self.create_node(to_xml_er, node, obj.clientId, 'clientId')
		self.create_node(to_xml_er, node, obj.destination, 'destination')
		self.create_node(to_xml_er, node, obj.headers, 'headers')
		self.create_node(to_xml_er, node, obj.messageId, 'messageId')
		self.create_node(to_xml_er, node, obj.timestamp, 'timestamp')
		self.create_node(to_xml_er, node, obj.timeToLive, 'timeToLive')

		self.create_node(to_xml_er, node, obj.clientId, 'clientId')
		self.create_node(to_xml_er, node, obj.messageId, 'messageId')

		self.create_node(to_xml_er, node, obj.flag3, 'flag3')

		self.create_node(to_xml_er, node, obj.correlationId, 'correlationId')
		self.create_node(to_xml_er, node, obj.correlationIdBytes, 'correlationIdBytes')

		self.to_xml_more(to_xml_er, obj, node)
	
	def to_xml_more(self, to_xml_er, obj, node):
		raise NotImplementedError('subclass me!')

	def create_node(self, to_xml_er, parent, value, tag):
		if value is not None:
			to_xml_er.create_value_node(parent, value, tag)
		else:
			to_xml_er.create_child(parent, tag)

	def from_xml(self, from_xml_er, obj, value_node):
		nodes = from_xml_er.get_children(value_node)
		node_iter = iter(nodes)

		obj.flag1              = self.read_node(from_xml_er, node_iter.next())
		obj.flag2              = self.read_node(from_xml_er, node_iter.next())
		obj.body               = self.read_node(from_xml_er, node_iter.next())
		obj.clientId           = self.read_node(from_xml_er, node_iter.next())
		obj.destination        = self.read_node(from_xml_er, node_iter.next())
		obj.headers            = self.read_node(from_xml_er, node_iter.next())
		obj.messageId          = self.read_node(from_xml_er, node_iter.next())
		obj.timestamp          = self.read_node(from_xml_er, node_iter.next())
		obj.timeToLive         = self.read_node(from_xml_er, node_iter.next())
		obj.clientId           = self.read_node(from_xml_er, node_iter.next())
		obj.messageId          = self.read_node(from_xml_er, node_iter.next())
		obj.flag3              = self.read_node(from_xml_er, node_iter.next())
		obj.correlationId      = self.read_node(from_xml_er, node_iter.next())
		obj.correlationIdBytes = self.read_node(from_xml_er, node_iter.next())

		self.from_xml_more(from_xml_er, obj, node_iter)

	def from_xml_more(self, from_xml_er, obj, node_iter):
		raise NotImplementedError('subclass me!')

	def read_node(self, from_xml_er, node):
		if from_xml_er.get_attribute(node, 'class') is None:
			return None
		else:
			return from_xml_er.get_value(node)


class BlazeDSAsyncMessageXMLer(BlazeDSAbstractMessageXMLer):

	def __init__(self):
		BlazeDSAbstractMessageXMLer.__init__(self)

	def to_xml_more(self, to_xml_er, obj, node):
		pass

	def from_xml_more(self, from_xml_er, obj, node_iter):
		pass

class BlazeDSAcknowledgeMessageXMLer(BlazeDSAbstractMessageXMLer):

	def __init__(self):
		BlazeDSAbstractMessageXMLer.__init__(self)

	def to_xml_more(self, to_xml_er, obj, node):
		pass

	def from_xml_more(self, from_xml_er, obj, node_iter):
		pass

class BlazeDSCommandMessageXMLer(BlazeDSAbstractMessageXMLer):

	def __init__(self):
		BlazeDSAbstractMessageXMLer.__init__(self)

	def to_xml(self, to_xml_er, obj, parent):
		BlazeDSAbstractMessageXMLer.to_xml(self, to_xml_er, obj, parent)

	def from_xml(self, from_xml_er, obj, value_node):
		BlazeDSAbstractMessageXMLer.from_xml(self, from_xml_er, obj, value_node)

	def to_xml_more(self, to_xml_er, obj, node):
		self.create_node(to_xml_er, node, obj.operation, 'operation')

	def from_xml_more(self, from_xml_er, obj, node_iter):
		obj.operation = self.read_node(from_xml_er, node_iter.next())

register_predefined_ext_xmlers()


