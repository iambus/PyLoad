
import Playable
import Evalable

class Player(Playable.Playable, Evalable.Scoped):
	def __init__(self):
		Playable.Playable.__init__(self)
		Evalable.Scoped.__init__(self)

		self.beforescript = Evalable.Script('')
		self.afterscript = Evalable.Script('')


	def play(self, basescope = None):
		if basescope == None:
			basescope = self.scope
		self.before(basescope)
		self.playmain(basescope)
		self.after(basescope)

	def before(self, basescope = None):
		self.execute_script(self.beforescript, basescope)

	def execute(self, basescope = None):
		self.play(basescope)

	def playmain(self, basescope):
		Evalable.Scoped.execute(self, basescope)

	def after(self, basescope = None):
		self.execute_script(self.afterscript, basescope)


class Controller:
	pass


if __name__ == '__main__':
	player = Player()
	player.beforescript = Evalable.Script('print "before"')
	player.afterscript = Evalable.Script('print "after"')
	player.play()

