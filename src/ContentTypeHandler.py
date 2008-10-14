
import re
import Coder

# immutable: dirty hack
# XXX: how to implement an immutable instance in Python?
class ContentTypeHandler(tuple):
	def __new__(self, coder = Coder.EmptyCoder, syntax = None):
		if syntax == None:
			import editor.syntax.default
			syntax = editor.syntax.default
		from editor.Syntax import Syntax
		return tuple.__new__(self, (coder, Syntax(syntax)))

	def get_coder(self):
		return self.coder

	def get_syntax(self):
		return self.syntax

	def get(self):
		return (self.coder, self.syntax)

	def __getattr__(self, name):
		if name == 'coder':
			return self[0]
		if name == 'syntax':
			return self[1]
		raise AttributeError("No attribute "+name)

	def __setattr__(self, name, v):
		raise AttributeError("ContentTypeHandler is immutable")

	#FIXME: maybe not good enough...
	def __deepcopy__(self, ignored):
		return ContentTypeHandler(self.coder, self.syntax)


def get_handler(content):
	import editor.syntax.default
	import editor.syntax.html
	import editor.syntax.xml
	import editor.syntax.python
	mapping = {
			'default' : ContentTypeHandler(Coder.EmptyCoder, editor.syntax.default),
			'html' : ContentTypeHandler(Coder.EmptyCoder, editor.syntax.html),
			'xml' : ContentTypeHandler(Coder.EmptyCoder, editor.syntax.xml),
			'amf' : ContentTypeHandler(Coder.AMFCoder, editor.syntax.xml),
			'python' : ContentTypeHandler(Coder.EmptyCoder, editor.syntax.python),
			}

	m = re.search(r'^content-type:\s*(.*)', content, re.I|re.M)
	if m:
		type = m.group(1)
		if   re.search(r'application/x-amf', type, re.I):
			return mapping['amf']
		elif re.search(r'xml', type, re.I):
			return mapping['xml']
		elif re.search(r'html', type, re.I):
			return mapping['html']
		elif re.search(r'text', type, re.I):
			return mapping['default']
		else:
			return mapping['default']
	return ContentTypeHandler()

if __name__ == '__main__':
	h = ContentTypeHandler()

