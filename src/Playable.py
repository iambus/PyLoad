
import Repository

class Playable(Repository.Mixin):
	def __init__(self):
		# register uuid
		Repository.Mixin.__init__(self)
	
	def play(self):
		raise NotImplementedError()


if __name__ == '__main__':
	Playable().play()

