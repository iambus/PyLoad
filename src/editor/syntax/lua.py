
import wx.stc

LEXER = wx.stc.STC_LEX_LUA
OPERATOR = wx.stc.STC_LUA_OPERATOR

Prefix = 'STC_LUA_'

# keyword
word = ( 'and', 'break', 'do', 'else', 'elseif', 'end', 'false', 'for', 'function', 'if', 'in', 'local', 'nil', 'not', 'or', 'repeat', 'return', 'then', 'true', 'until', 'while',)

# library
word2 = (
	'coroutine',
	'debug',
	'io',
	'math',
	'os',
	'package',
	'string',
	'table',
	)

# library method
word3 = (
	'package.cpath',
	'package.loaded',
	'package.loadlib',
	'package.path',
	'package.preload',
	'package.seeall',
	'coroutine.running',
	'coroutine.create',
	'coroutine.resume',
	'coroutine.status',
	'coroutine.wrap',
	'coroutine.yield',
	'string.byte',
	'string.char',
	'string.dump',
	'string.find',
	'string.len',
	'string.lower',
	'string.rep',
	'string.sub',
	'string.upper',
	'string.format',
	'string.gsub',
	'string.gfind',
	'table.getn',
	'table.setn',
	'table.foreach',
	'table.foreachi',
	'string.gmatch',
	'string.match',
	'string.reverse',
	'table.maxn',
	'table.concat',
	'table.sort',
	'table.insert',
	'table.remove',
	'math.abs',
	'math.acos',
	'math.asin',
	'math.atan',
	'math.atan2',
	'math.ceil',
	'math.sin',
	'math.cos',
	'math.tan',
	'math.deg',
	'math.exp',
	'math.floor',
	'math.log',
	'math.log10',
	'math.max',
	'math.min',
	'math.mod',
	'math.fmod',
	'math.modf',
	'math.cosh',
	'math.sinh',
	'math.tanh',
	'math.pow',
	'math.rad',
	'math.sqrt',
	'math.frexp',
	'math.ldexp',
	'math.random',
	'math.randomseed',
	'math.pi',
	'io.stdin',
	'io.stdout',
	'io.stderr',
	'io.close',
	'io.flush',
	'io.input',
	'io.lines',
	'io.open',
	'io.output',
	'io.popen',
	'io.read',
	'io.tmpfile',
	'io.type',
	'io.write',
	'os.clock',
	'os.date',
	'os.difftime',
	'os.execute',
	'os.exit',
	'os.getenv',
	'os.remove',
	'os.rename',
	'os.setlocale',
	'os.time',
	'os.tmpname',
	'debug.debug',
	'debug.gethook',
	'debug.getinfo',
	'debug.getlocal',
	'debug.getupvalue',
	'debug.setlocal',
	'debug.setupvalue',
	'debug.sethook',
	'debug.traceback',
	'debug.getfenv',
	'debug.getmetatable',
	'debug.getregistry',
	'debug.setfenv',
	'debug.setmetatable',
	)

# function
word4 = (
	'assert', 'collectgarbage', 'dofile', 'error', 'next',
	'print', 'rawget', 'rawset', 'tonumber', 'tostring', 'type', '_VERSION',
	'_ALERT', '_ERRORMESSAGE', 'gcinfo',
	'call', 'copytagmethods', 'dostring',
	'foreach', 'foreachi', 'getglobal', 'getn',
	'gettagmethod', 'globals', 'newtag',
	'setglobal', 'settag', 'settagmethod', 'sort',
	'tag', 'tinsert', 'tremove',
	'_INPUT', '_OUTPUT', '_STDIN', '_STDOUT', '_STDERR',
	'openfile', 'closefile', 'flush', 'seek',
	'setlocale', 'execute', 'remove', 'rename', 'tmpname',
	'getenv', 'date', 'clock', 'exit',
	'readfrom', 'writeto', 'appendto', 'read', 'write',
	'PI', 'abs', 'sin', 'cos', 'tan', 'asin',
	'acos', 'atan', 'atan2', 'ceil', 'floor',
	'mod', 'frexp', 'ldexp', 'sqrt', 'min', 'max', 'log',
	'log10', 'exp', 'deg', 'rad', 'random',
	'randomseed', 'strlen', 'strsub', 'strlower', 'strupper',
	'strchar', 'strrep', 'ascii', 'strbyte',
	'format', 'strfind', 'gsub',
	'getinfo', 'getlocal', 'setlocal', 'setcallhook', 'setlinehook',
	'_G', 'getfenv', 'getmetatable', 'ipairs', 'loadfile',
	'loadstring', 'pairs', 'pcall', 'rawequal',
	'require', 'setfenv', 'setmetatable', 'unpack', 'xpcall',
	'gcinfo', 'loadlib', 'LUA_PATH', '_LOADED', '_REQUIREDNAME',
	'load', 'module', 'select',
	)

#
word5 = ()

#
word6 = ()

#
word7 = ()

#
word8 = ()



