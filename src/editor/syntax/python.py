
import wx.stc

LEXER = wx.stc.STC_LEX_PYTHON
OPERATOR = wx.stc.STC_P_OPERATOR

Prefix = 'STC_P_'

# keyword
word = ('break', 'continue', 'del', 'except', 'exec', 'finally', 'pass', 'print', 'raise', 'return', 'try', 'global', 'assert', 'lambda', 'yield', 'def', 'class', 'for', 'while', 'if', 'elif', 'else', 'and', 'in', 'is', 'not', 'or', 'import', 'from', 'as', )


# library
word2 = (
	)

# library method
word3 = (
	)

# function
word4 = (
'True', 'False', 'bool', 'enumerate', 'set', 'frozenset', 'help', 'reversed', 'sorted', 'sum', 'Ellipsis', 'None', 'NotImplemented', '__import__', 'abs', 'apply', 'buffer', 'callable', 'chr', 'classmethod', 'cmp', 'coerce', 'compile', 'complex', 'delattr', 'dict', 'dir', 'divmod', 'eval', 'execfile', 'file', 'filter', 'float', 'getattr', 'globals', 'hasattr', 'hash', 'hex', 'id', 'input', 'int', 'intern', 'isinstance', 'issubclass', 'iter', 'len', 'list', 'locals', 'long', 'map', 'max', 'min', 'object', 'oct', 'open', 'ord', 'pow', 'property', 'range', 'raw_input', 'reduce', 'reload', 'repr', 'round', 'setattr', 'slice', 'staticmethod', 'str', 'super', 'tuple', 'type', 'unichr', 'unicode', 'vars', 'xrange', 'zip',

	)

# class
word5 = (
'ArithmeticError', 'AssertionError', 'AttributeError', 'DeprecationWarning', 'EOFError', 'EnvironmentError', 'Exception', 'FloatingPointError', 'IOError', 'ImportError', 'IndentationError', 'IndexError', 'KeyError', 'KeyboardInterrupt', 'LookupError', 'MemoryError', 'NameError', 'NotImplementedError', 'OSError', 'OverflowError', 'OverflowWarning', 'ReferenceError', 'RuntimeError', 'RuntimeWarning', 'StandardError', 'StopIteration', 'SyntaxError', 'SyntaxWarning', 'SystemError', 'SystemExit', 'TabError', 'TypeError', 'UnboundLocalError', 'UnicodeError', 'UnicodeEncodeError', 'UnicodeDecodeError', 'UnicodeTranslateError', 'UserWarning', 'ValueError', 'Warning', 'WindowsError', 'ZeroDivisionError',
		)

#
word6 = ()

#
word7 = ()

#
word8 = ()



