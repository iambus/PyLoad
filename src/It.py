

#TODO: thread-safe
class It:
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

