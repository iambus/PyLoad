
import Player

class Special(Player.Player):
	def __init__(self):
		Player.Player.__init__(self)

	def set_host(self, host):
		seen = []
		def set_your_host(node, host):
			if node in seen:
				return
			seen.append(node)
			if hasattr(node, 'set_host'):
				node.set_host(host)
				return
			else:
				for child in node.childern:
					set_your_host(child, host)
		for c in self.childern:
			set_your_host(c, host)

