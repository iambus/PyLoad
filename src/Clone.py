
import copy

def simple_clone(src):
	return copy.copy(src)

def simple_deep_clone(src):
	return copy.deepcopy(src)

def walk_tree_in_repository(tree, func):
	seen = set()

	import types
	immutable_classes = (
			type(None),
			int, long, float, bool, str, unicode,
			# tuple, #iterable
			# list, #not immutable
			# dict, #not immutable
			# frozenset, #iterable
			type, xrange, types.ClassType,
			types.BuiltinFunctionType,
			types.FunctionType,
			types.MethodType,
			types.ModuleType,
			)

	def set_uuid(obj):
		import Repository
		if id(obj) in seen:
			return
		if not hasattr(obj, '__class__'):
			return
		c = obj.__class__
		if c in immutable_classes:
			return
		seen.add(id(obj))
		if isinstance(obj, Repository.Mixin):
			func(obj)
		if c == dict:
			for k, v in obj.items():
				set_uuid(k)
				set_uuid(v)
			return
		if hasattr(obj, '__iter__'):
			for i in obj:
				set_uuid(i)
		for attr in dir(obj):
			if attr.startswith('__'):
				continue
			set_uuid(getattr(obj, attr))

	set_uuid(tree)



def clone(src, repository = None):
	dest = copy.deepcopy(src)
	
	def register_obj(obj):
		if repository:
			obj.register_self_in(repository)
		else:
			obj.register_self()
	walk_tree_in_repository(dest, register_obj)
	return dest


def clone_for_special(src):
	from Record import Record, Page, Hit
	from Player import Player

	cloneable = []
	uncloneable = [Record, Page, Hit]

	if src.__class__ in uncloneable:
		return None

	def replace_with_uuid(node):
		assert node.__class__ not in uncloneable
		if isinstance(node, Player):
			for i in range(len(node.childern)):
				if node.childern[i].__class__ in uncloneable:
					node.childern[i] = node.childern[i].uuid
				else:
					replace_with_uuid(node.childern[i])
			for i in range(len(node.scripts)):
				if node.scripts[i].__class__ in uncloneable:
					node.scripts[i] = node.scripts[i].uuid
				else:
					replace_with_uuid(node.scripts[i])

	def replace_uuid_back(node):
		import Repository
		assert node.__class__ not in uncloneable
		if isinstance(node, Player):
			for i in range(len(node.childern)):
				if type(node.childern[i]) in (str, unicode):
					node.childern[i] = Repository.lookup(node.childern[i])
				else:
					replace_uuid_back(node.childern[i])
			for i in range(len(node.scripts)):
				if type(node.scripts[i]) in (str, unicode):
					node.scripts[i] = Repository.lookup(node.scripts[i])
				else:
					replace_uuid_back(node.scripts[i])

	replace_with_uuid(src)
	dest = clone(src)
	replace_uuid_back(src)
	replace_uuid_back(dest)

	return dest


if __name__ == '__main__':
	import Player
	player = Player.Player()
	s1 = Player.Script()
	s2 = Player.Script()
	player.add_child(s1)
	player.add_child(s2)
	player.add_script(s1)
	new_player = clone(player)
	print new_player
	print new_player.beforescript.uuid
	import Record
	h = Record.Hit('')
	clone(h)

