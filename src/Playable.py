

class Playable:
	def __init__(self):
		pass
	
	def play(self):
		raise NotImplementedError()


if __name__ == '__main__':
	Playable().play()

