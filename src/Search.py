
from Record import Record, Page, Hit
from Controller import If, Loop, Block
from Special import Special
from Player import Script



def matchString(keyword, text):
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

