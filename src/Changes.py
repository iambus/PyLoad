
changed = False

def is_changed():
	return changed

def set_changed(b = True):
	global changed
	changed = b

	global callbacks
	for callback in callbacks:
		callback(changed)

def change():
	set_changed(True)

def unchange():
	set_changed(False)

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


# change notification
callbacks = []
def register_changed_callback(callback):
	global callbacks
	callbacks.append(callback)

if __name__ == '__main__':
	pass

