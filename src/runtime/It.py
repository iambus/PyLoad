
import threading

class It:
	'Thread-safe'
	def __init__(self, seq):
		self.iterator = iter(seq)
		self.lock = threading.Lock()

	def __call__(self):
		if self.lock == None:
			# stopped
			return None
		lock = self.lock
		lock.acquire()
		try:
			return self.iterator.next()
		except StopIteration:
			self.lock = None
			return None
		finally:
			lock.release()

class LocalIt:
	'Thread-unsafe'
	def __init__(self, seq):
		self.iterator = iter(seq)

	def __call__(self):
		try:
			return self.iterator.next()
		except StopIteration:
			return None

if __name__ == '__main__':
	it = It([1, 2, 3])
	print it()
	print it()
	print it()
	print it()

