
import re
import wx

DEFAULT_FONT = 'Courier New'

def CheckFontFace(face):
	fontAttrs = (10, wx.SWISS, wx.NORMAL, wx.NORMAL, False)
	font = wx.Font(*fontAttrs)
	return face if font.SetFaceName(face) else DEFAULT_FONT

def LoadConfigDictFromFile(filepath):
	try:
		fp = open(filepath, 'r')
	except IOError, e:
		print e
		return {}

	d = {}
	ds = {}
	assign = re.compile(r'^(\w+)\s*=\s*(.*)$')
	style = re.compile(r'^(\w+)\s*:\s*(.*)$')
	ev = re.compile(r'\$(\w+)')
	bi = re.compile(r'^[0-9A-Z_]+$')
	for line in fp:
		if assign.match(line):
			m = assign.match(line)
			k = m.group(1)
			v = m.group(2)
			v = v.strip('\'\" \t\r')
			if k == 'font':
				d[k] = CheckFontFace(v)
			else:
				d[k] = v
		elif style.match(line):
			m = style.match(line)
			k = m.group(1)
			if not bi.match(k):
				k = k.lower()
			v = m.group(2)
			v = v.strip('\'\" \t\r')
			v = ev.sub(r'%(\1)s', v) % d
			ds[k] = v
	fp.close()
	return ds



def ParseTextAttrToDict(s):
	s = s.lower()
	d = {}
	attrs = re.split(r'\s*,\s*', s)
	for a in attrs:
		kv = a.split(':')
		assert len(kv) == 1 or len(kv) == 2
		if len(kv) == 1:
			v = kv[0]
			if v == 'bold':
				d['bold'] = True
			else:
				d['fore'] = v
		else:
			k, v = kv
			d[k] = v
	return d

def CreateFont(fontAttrs):
	font = wx.Font(*fontAttrs[:5])
	if not font.SetFaceName(fontAttrs[5]):
		font.SetFaceName(DEFAULT_FONT)
	return font

def ParseFont(s):
	d = ParseTextAttrToDict(s)
	fontAttrs = [10, wx.SWISS, wx.NORMAL, wx.NORMAL, False, DEFAULT_FONT]

	if d.has_key('bold'):
		fontAttrs[3] = wx.BOLD
	if d.has_key('face'):
		fontAttrs[5] = d['face']

	return CreateFont(fontAttrs)

def ParseTextAttr(s):
	d = ParseTextAttrToDict(s)
	fore = wx.NullColour
	back = wx.NullColour
	fontAttrs = [10, wx.SWISS, wx.NORMAL, wx.NORMAL, False, DEFAULT_FONT]

	if d.has_key('bold'):
		fontAttrs[3] = wx.BOLD
	if d.has_key('face'):
		fontAttrs[5] = d['face']
	if d.has_key('fore'):
		fore = d['fore']
	if d.has_key('back'):
		back = d['back']

	font = CreateFont(fontAttrs)
	return wx.TextAttr(fore, back, font)


