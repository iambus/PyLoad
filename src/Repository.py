

# Deprecated
def uuid_generator_generator():
	'Internal usage'
	import threading
	lock = threading.Lock()

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

# Deprecated
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

# Deprecated
class Repository:
	def __init__(self):
		self.uuid = uuid_generator_generator()
		self.lookup, self.register = table_generator()

class RepositoryInternal:
	def __init__(self):
		self.uuid_counter = 0
		self.mappings = {}

class Repository:
	def __init__(self):
		import threading
		self.lock = threading.Lock()
		self.data = RepositoryInternal()
	
	def uuid(self):
		self.lock.acquire()
		try:
			return 'u%05d' % self.data.uuid_counter
		finally:
			self.data.uuid_counter += 1
			self.lock.release()

	def lookup(self, uuid):
		assert type(uuid) == str
		self.lock.acquire()
		try:
			return self.data.mappings[uuid]
		finally:
			self.lock.release()
	
	def register(self, uuid, v):
		assert type(uuid) == str
		self.lock.acquire()
		try:
			self.data.mappings[uuid] = v
		finally:
			self.lock.release()


global_repository = Repository()
uuid, lookup, register = global_repository.uuid, global_repository.lookup, global_repository.register

def get_global_repository():
	global global_repository
	return global_repository

def set_global_repository(repository):
	global global_repository
	global uuid, lookup, register 
	old_global_repository = global_repository
	global_repository = repository
	uuid, lookup, register = repository.uuid, repository.lookup, repository.register
	return old_global_repository

def register_object(obj):
	id = uuid()
	register(id, obj)
	return id

class Mixin:
	def __init__(self):
		self.register_self()

	def register_self(self):
		"This method can be called by cloned objects to register themselves as new objects."
		self.uuid = uuid()
		register(self.uuid, self)

if __name__ == '__main__':
	print uuid()
	print uuid()
	register('x', 'hehe')
	print lookup('x')
	Mixin()

