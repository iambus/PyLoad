
from SimpleXMLTree import IXMLTree

from lxml import etree

class LXMLTree(IXMLTree):
	def __init__(self, tag = None):
		IXMLTree.__init__(self, tag)

	def init_root(self, tag):
		self.root = etree.Element(tag)
		return self.root

	def get_root_node(self):
		return self.root

	def create_child(self, parent, tag):
		return etree.SubElement(parent, tag)

	def get_children(self, node):
		return list(node)

	def set_text(self, node, value):
		try:
			value = str(value)
		except UnicodeEncodeError:
			if type(value) == unicode:
				# keep it as unicode
				pass
			else:
				raise
		if len(value) > 40 and ('<' in value) and (']]>' not in value):
			# FIXME: how to reserve \r?
			node.text = etree.CDATA(value)
		else:
			node.text = value

	def get_text(self, node):
		text = node.text
		if node.text == None:
			text = ''
		return text

	def set_attribute(self, node, name, value):
		node.set(name, value)

	def get_attribute(self, node, name):
		return node.get(name)

	def get_tag(self, node):
		return node.tag

	def tostring(self):
		pretty = etree.tostring(self.root, pretty_print=True, encoding='utf-8')
		return pretty

	@classmethod
	def fromstring(cls, text):
		tree = cls()

		# XXX: encoding?
		tree.root = etree.fromstring(text)

		return tree

