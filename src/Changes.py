
changed = False

def is_changed():
	return changed

def change():
	global changed
	changed = True

def unchange():
	global changed
	changed = False

def reset():
	unchange()

def test():
	return is_changed()

# decorator
def make_change(func):
	def decorator(*__args,**__kw):
		change()
		return func(*__args, **__kw)
	return decorator

# decorator
def remove_change(func):
	def decorator(*__args,**__kw):
		try:
			return func(*__args, **__kw)
		finally:
			unchange()
	return decorator

if __name__ == '__main__':
	pass

