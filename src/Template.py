

def escape(s):
	return s.replace('$', '$$')

def subst(template, variables):
	from string import Template
	return Template(template).safe_substitute(variables)

def eval(template, variables):
	raise NotImplementedError('eval is not implemented')

if __name__ == '__main__':
	print subst('${x+y},$y', {'x':[1, 2], 'y':'2'})

