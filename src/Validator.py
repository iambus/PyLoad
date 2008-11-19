
from Errors import ValidationError


class Validator:
	@classmethod
	def validate(cls, x):
		raise NotImplementedError()

class ResponseValidator(Validator):
	pass

class DefaultResponseValidator(ResponseValidator):
	@classmethod
	def validate(cls, response):
		# TODO: validate HTTP response code
		pass

class AMFResponseValidator(ResponseValidator):
	@classmethod
	def validate(cls, response):
		try:
			if response.rawfind('flex.messaging.messages.ErrorMessage'):
				members = response.xfindall('.//members/member')
				messages = {}
				for m in members:
					if m.attrib['class'] == 'str':
						name = m.attrib['name']
						if name in ['faultCode', 'destination', 'faultString']:
							messages[name] = m.text.strip()
						# ignore others
						#elif name not in ['clientId', 'messageId', 'correlationId']:
						#	messages[name] = m.text.strip()
				raise ValidationError(messages)
			else:
				# no error
				pass
		except Exception, e:
			if isinstance(e, ValidationError):
				raise
			else:
				import sys
				ValidationError(e, sys.exc_info()[2]).rethrow()


