
from Record import Record, Page, Hit
from Controller import If, Loop, Block
from Special import Special
from Player import Script


def to_unicode(text):
	if type(text) == unicode:
		return text
	encodings = ["utf-8", "gbk"]
	try:
		return unicode(text)
	except:
		pass
	for encoding in encodings:
		try:
			return unicode(text, encoding)
		except:
			pass
	return None

def matchString(keyword, text):
	if type(keyword) != type(text):
		ukeyword = to_unicode(keyword)
		utext = to_unicode(text)
		if ukeyword == None:
			print "Cannot decode keyword: ", keyword
			return None
		if utext == None:
			print "Cannot decode text: ", text
			return None
		keyword = ukeyword
		text = utext
	return keyword.lower() in text.lower()

def matchLabel(keyword, data):
	return matchString(keyword, data.label) or matchString(keyword, data.uuid)

def matchScript(keyword, script):
	return matchString(keyword, script.script)

def matchCondition(keyword, data):
	return matchString(keyword, data.condition.script)

def matchBeforeAfter(keyword, data):
	return matchString(keyword, data.beforescript.script) or\
	       matchString(keyword, data.afterscript.script)

def matchRequest(keyword, hit):
	return matchString(keyword, hit.url) or \
	       matchString(keyword, hit.reqstr) or\
	       (hit.respstr and matchString(keyword, hit.respstr))


attrDict = {
	Record:  (matchLabel, matchBeforeAfter),
	Page:    (matchLabel, matchBeforeAfter),
	Hit:     (matchLabel, matchBeforeAfter, matchRequest),
	If:      (matchLabel, matchBeforeAfter, matchCondition),
	Loop:    (matchLabel, matchBeforeAfter, matchCondition),
	Block:   (matchLabel, matchBeforeAfter),
	Special: (matchLabel, matchBeforeAfter),
	Script:  (matchLabel, matchScript),
	}



def match(keyword, data):
	funcs = attrDict[data.__class__]
	for func in funcs:
		if func(keyword, data):
			return True

