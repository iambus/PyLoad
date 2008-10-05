
import copy

def simple_clone(src):
	return copy.copy(src)

def simple_deep_clone(src):
	return copy.deepcopy(src)

def clone(src):
	dest = copy.deepcopy(src)
	seen = []

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
		if obj in seen:
			return
		if not hasattr(obj, '__class__'):
			return
		c = obj.__class__
		if c in immutable_classes:
			return
		seen.append(obj)
		if isinstance(obj, Repository.Mixin):
			obj.register_self()
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

	set_uuid(dest)
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

