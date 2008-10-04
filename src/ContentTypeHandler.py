
import re
import Coder
import editor.syntax.default
import editor.syntax.html
import editor.syntax.xml
import editor.syntax.python

class ContentTypeHandler:
	def __init__(self, coder = Coder.EmptyCoder, syntax = editor.syntax.default):
		self.coder = coder
		self.syntax = syntax

	def get_coder(self):
		return self.coder

	def get_syntax(self):
		return self.syntax

	def get(self):
		return (self.coder, self.syntax)

mapping = {
		'default' : (Coder.EmptyCoder, editor.syntax.default),
		'html' : (Coder.EmptyCoder, editor.syntax.html),
		'xml' : (Coder.EmptyCoder, editor.syntax.xml),
		'amf' : (Coder.EmptyCoder, editor.syntax.xml),
		'python' : (Coder.EmptyCoder, editor.syntax.python),
		}

def get_handler(content):
	handler = ContentTypeHandler()
	m = re.search(r'^content-type:\s*(.*)', content, re.I|re.M)
	if m:
		type = m.group(1)
		if   re.search(r'application/x-amf', type, re.I):
			(handler.coder, handler.syntax) = mapping['amf']
		elif re.search(r'xml'              , type, re.I):
			(handler.coder, handler.syntax) = mapping['xml']
		elif re.search(r'html'             , type, re.I):
			(handler.coder, handler.syntax) = mapping['html']
		elif re.search(r'text'             , type, re.I):
			(handler.coder, handler.syntax) = mapping['default']
		else:
			(handler.coder, handler.syntax) = mapping['default']
			(handler.coder, handler.syntax) = mapping['default']
	return handler


