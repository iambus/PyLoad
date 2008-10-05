

class Syntax:
	def __init__(self, module):
		attrs = (
			'LEXER',
			'OPERATOR',
			'Prefix',
			'word',
			'word2',
			'word3',
			'word4',
			'word5',
			'word6',
			'word7',
			'word8',
		)
		for attr in attrs:
			setattr(self, attr, getattr(module, attr))

if __name__ == '__main__':
	import syntax.lua
	s = Syntax(syntax.lua)
	print dir(s)

