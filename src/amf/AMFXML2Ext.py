
from AMFExtAlias import find_alias

XMLER_MAP = {}

def register_ext_xmler(alias, xmler):
	XMLER_MAP[alias] = xmler

def register_predefined_ext_xmlers():
	register_ext_xmler('flex.messaging.io.ArrayCollection', DefaultXMLer())

def find_xmler(obj):
	return XMLER_MAP[obj]


class DefaultXMLer:
	def __init__(self):
		pass

	def to_xml(self, to_xml_er, obj, node):
		to_xml_er.create_value_node(node, obj.value)

	def from_xml(self, from_xml_er, obj, value_node):
		obj.value = from_xml_er.get_value(value_node)


register_predefined_ext_xmlers()


