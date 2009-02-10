
__all__ = ['register_alias', 'find_alias']

from AMFTypes import *

ALIAS_MAP = {}

def register_alias(alias, ext_type):
	ALIAS_MAP[alias] = ext_type

def register_alias_for(ext_type):
	register_alias(ext_type.CLASS_ALIAS, ext_type)

def register_predefined_aliases():
	register_alias('flex.messaging.io.ArrayCollection', DefaultExtObject)

def find_alias(alias):
	return ALIAS_MAP[alias]


class DefaultExtObject(ExtObject):
	def __init__(self, trait):
		ExtObject.__init__(self, trait)
		self.value = None

	def decode(self, decoder):
		self.value = decoder.read_value()

	def encode(self, encoder):
		encoder.write_value(self.value)

	def __str__(self):
		trait = self.trait.get_referenced()
		assert trait.__class__ == TraitExt
		return "ext-object<{%s}>=(%s)" % (trait, self.value)

	def __repr__(self):
		return str(self)

class BlazeDSAbstractMessage(ExtObject):
	def __init__(self):
		raise NotImplementedError()

	def decode(self, decoder):
		raise NotImplementedError()

	def encode(self, encoder):
		raise NotImplementedError()



register_predefined_aliases()


