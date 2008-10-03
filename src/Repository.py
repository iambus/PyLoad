

def uuid_generator_generator():
	'Internal usage'
	import threading
	lock = threading.Lock()
	uuid_counter = 0

	def uuid_generator():
		i = 0
		while i < 999999:
			yield 'u%05d' % i
			i = i + 1
		assert False, 'Max uuid reached'

	guuid = uuid_generator()

	def uuid():
		lock.acquire()
		try:
			return guuid.next()
		finally:
			lock.release()

	return uuid

uuid = uuid_generator_generator()

def table_generator():
	'Internal usage'
	import threading
	lock = threading.Lock()
	mappings = {}
	
	def lookup(uuid):
		assert type(uuid) == str
		lock.acquire()
		try:
			return mappings[uuid]
		finally:
			lock.release()
	
	def register(uuid, v):
		assert type(uuid) == str
		lock.acquire()
		try:
			mappings[uuid] = v
		finally:
			lock.release()

	return (lookup, register)

lookup, register = table_generator()

def register_object(obj):
	id = uuid()
	register(id, obj)
	return id

class Mixin:
	def __init__(self):
		self.uuid = uuid()
		register(self.uuid, self)

if __name__ == '__main__':
	print uuid()
	print uuid()
	register('x', 'hehe')
	print lookup('x')
	Mixin()

