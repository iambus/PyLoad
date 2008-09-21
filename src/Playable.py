

class Playable:
	def __init__(self):
		pass
	
	def play(self):
		self.before()
		self.playmain()
		self.after()

	def before(self):
		pass
	
	def playmain(self):
		pass
	
	def after(self):
		pass

if __name__ == '__main__':
	Playable().play()

