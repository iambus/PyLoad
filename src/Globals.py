
_G = {}
_G['_G'] = _G

def get_globals():
	return _G

def put_global(name, value):
	pass

def copy_globals():
	import copy
	x = copy.copy(_G)
	x['_G'] = x
	return x

if __name__ == '__main__':
	print get_globals()
	print copy_globals()


