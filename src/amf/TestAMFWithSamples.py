
import unittest

from AMFDecoder import AMFDecoder
from AMFEncoder import AMFEncoder
from AMFXML2 import FromXML, ToXML

##################################################
# {{{ Used to convert a file to repr-like string/file
def repr_file(path, topath = None):
	fp = open(path, 'rb')
	s = fp.read(32)
	lines = []
	while s:
		line = repr(s)
		line = line[1:-1]
		lines.append(line)
		s = fp.read(32)
	all = 'def get_data_():\n\treturn \\\n"' + '\\\n'.join(lines) + '";'
	fp.close()
	if topath:
		fp = open(topath, 'wb')
		fp.write(all)
		fp.close()
	return all
# }}}
##################################################
# {{{ Sample data

# client ping
def get_data_1():
	return \
"\x00\x03\x00\x00\x00\x01\x00\x04null\x00\x02/1\x00\x00\x00\xcb\n\x00\x00\x00\x01\x11\n\x81\x13Mfl\
ex.messaging.messages.CommandMes\
sage\x13operation\x1bcorrelationId\x0fhea\
ders\x17destination\x13timestamp\tbody\x11\
clientId\x15timeToLive\x13messageId\x04\x05\x06\
\x01\n\x0b\x01\tDSId\x06\x07nil\x01\x06\x01\x04\x00\n\x05\x01\x01\x04\x00\x06IF19AE\
A22-8447-DD95-8C7A-D6424E55E232";

# client ping response
def get_data_2():
	return \
"\x00\x03\x00\x01\x00\x12AppendToGatewayUrl\x00\xff\xff\xff\xff\x02\x00,\
;jsessionid=84133E0430A2F71E91D6\
C712F6814079\x00\x01\x00\x0b/1/onResult\x00\x00\xff\xff\xff\
\xff\x11\n\x81\x03Uflex.messaging.messages.Ac\
knowledgeMessage\x17destination\x0fhea\
ders\x1bcorrelationId\x13messageId\x13tim\
estamp\x11clientId\x15timeToLive\tbody\x01\
\n\x13\x01\tDSId\x06I6717F1ED-FB0B-377A-46E\
9-7CDBC59DB8A3\x06IF19AEA22-8447-DD\
95-8C7A-D6424E55E232\x06I6717F1ED-F\
B2F-94B7-95F9-EE49F6B0FAC2\x05Bq\xcdd%\
R\xb0\x00\x06I6717F1ED-FB1E-4A71-2ECE-895\
21E76CF7F\x05\x00\x00\x00\x00\x00\x00\x00\x00\x01";

# login
def get_data_3():
	return \
"\x00\x03\x00\x00\x00\x01\x00\x04null\x00\x02/4\x00\x00\x01A\n\x00\x00\x00\x01\x11\n\x81\x13Ofl\
ex.messaging.messages.RemotingMe\
ssage\x13operation\rsource\x0fheaders\x17d\
estination\x13timestamp\tbody\x11client\
Id\x15timeToLive\x13messageId\x06\x0blogin\x01\n\
\x0b\x01\x15DSEndpoint\x06\rmy-amf\tDSId\x06I649F\
D9B4-5E19-45D7-46F9-46B4BC7CF647\
\x01\x06\x15SUMService\x04\x00\t\t\x01\x06\x13vtbaadmin\x06\rv\
itria\x02\x03\x06I649FDA27-1D0A-3A78-B34F\
-199A490800EF\x04\x00\x06I78D7B35B-F2E9-C\
8CE-D342-D53FF8536EBD";

# login response
def get_data_4():
	return \
"\x00\x03\x00\x00\x00\x01\x00\x0b/4/onResult\x00\x00\xff\xff\xff\xff\x11\n\x81\x03Ufl\
ex.messaging.messages.Acknowledg\
eMessage\x17destination\x0fheaders\x1bcor\
relationId\x13messageId\x13timestamp\x11c\
lientId\x15timeToLive\tbody\x01\n\x03\x01\x06I78D\
7B35B-F2E9-C8CE-D342-D53FF8536EB\
D\x06I64A1354F-2F0D-8AE3-2E16-A744B\
1DDF2B4\x05Bq\xcdS\xff\xb9\xf0\x00\x06I649FDA27-1D0A-\
3A78-B34F-199A490800EF\x05\x00\x00\x00\x00\x00\x00\x00\x00\n\
\x81\x13\x01\x13loginUser\x1fautoRefreshType#li\
censesPrivilege\x1dprivilegesInfo\x07b\
e1\x1bisAutoRefresh-WorkflowAccessi\
bleInfo\x13accessBEs\x1bisGlobalAdmin\n\
S3com.vitria.m3oui.sum.User\x0bphon\
e\risUser\x0bemail\tname\x05id\x01\x03\x01\x06/Vitri\
a BA administrator\x06\x13vtbaadmin\x06\x11r\
ealtime\t\x03\x01\x06\x030\n\x13\x01 \n\x05\n\x07Cflex.messa\
ging.io.ArrayCollection\t\x1d\x01\n\x82\x037co\
m.vitria.m3oui.core.Model\x11lcStat\
us\x19lcStatusDate\x15lcStatusBy\ttype\x11\
lockedBy\x11category\x15properties4\x15re\
ferences\x11contents\x1bremovedRefers\x19\
lcStatusNote\x0bflags\tpath2\x19removed\
Props\x01\x05\x00\x00\x00\x00\x00\x00\x00\x00\x01\x06\x1dKnowledgeSpace\
\x01\x01\n\x81\x13\x01\x17vt:lastDate\x19hasLifecycle%\
vtt:numberOfModels\x17vtui:hidden\x15r\
eleasable\x19vt:firstUser-vtt:model\
sLockedByUser\x17vt:lastUser\x19vt:fir\
stDate\x05Bq\xcdSn%\xf0\x00\x06\ttrue\x06<\x06\x0bfalse\x06r\
\x068\x06<\x068\x05Bq\xcdSn%\xf0\x00\x06Ia16c6311-7a5a-4\
79f-9a78-e31ff649fbf1\x01\n\x05\x01\x01\x04\x1f\x06?/v\
tbe197358/vtProcess1355134543\x06\x0fP\
rocess\x01\n\x19\x01\x05\x00\x00\x00\x00\x00\x00\x00\x00\x01\x06^\x01\x01\n\x81#\x01`bdf\
hljnp\x0fvtui:BE\x05Bq\xcdSn\xa0\x10\x00\x06r\x06\x0527\x06t\x06r\
\x06<\x068\x068\x05Bq\xcdSn\xa0\x10\x00\x06 \x06Ie77c7cd4-8d78\
-4bf7-bdbb-6f5769380157\x01\n\x05\x01\x01\x04\x1f\x06=\
/vtbe197358/vtSchema1824120383\x06\r\
Schema\x01\n\x19\x01\x05\x00\x00\x00\x00\x00\x00\x00\x00\x01\x06^\x01\x01\n\x1d\x05Bq\xcdSn\
\xd2\xe0\x00\x06t\x06<\x06t\x06t\x068\x06<\x068\x05Bq\xcdSn\xd2\xe0\x00\x06I4deb\
1535-2630-4e41-b97e-8142e68d7108\
\x01\n\x05\x01\x01\x04\x1f\x06C/vtbe197358/vtWorkgroup\
1193143826\x06\x13Workgroup\x01\n\x19\x01\x05\x00\x00\x00\x00\x00\x00\
\x00\x00\x01\x06^\x01\x01\n!\x05Bq\xcdSn\xdf\x90\x00\x06t\x06\x037\x06t\x06r\x06<\x068\x06\
8\x05Bq\xcdSn\xdf\x90\x00\x06 \x06I8ff21db7-cfc7-427a\
-825b-5ed54ceecdf1\x01\n\x05\x01\x01\x04\x1f\x063/vtbe\
197358/vtPage2479791\x06\tPage\x01\n\x19\x01\x05\x00\
\x00\x00\x00\x00\x00\x00\x00\x01\x06^\x01\x01\n\x1d\x05Bq\xcdSn\xed@\x00\x06r\x06<\x06t\x06r\x06\
8\x06<\x068\x05Bq\xcdSn\xed@\x00\x06I0162b214-0d53-40\
79-a093-75d55955c554\x01\n\x05\x01\x01\x04\x1f\x06=/vt\
be197358/vtService646160747\x06\x0fSer\
vice\x01\n\x19\x01\x05\x00\x00\x00\x00\x00\x00\x00\x00\x01\x06^\x01\x01\n!\x05Bq\xcdSn\xf7\x00\
\x00\x06t\x06\x0523\x06t\x06r\x06<\x068\x068\x05Bq\xcdSn\xf7\x00\x00\x06 \x06Ice\
83acf7-8e40-4dc2-adb5-2f66b68acb\
92\x01\n\x05\x01\x01\x04\x1f\x067/vtbe197358/vtQuery78\
391464\x06\x0bQuery\x01\n\x19\x01\x05\x00\x00\x00\x00\x00\x00\x00\x00\x01\x06^\x01\x01\n\
\x1d\x05Bq\xcdSn\xff\xd0\x00\x06r\x06\x034\x06t\x06r\x068\x06<\x068\x05Bq\xcdSn\xff\
\xd0\x00\x06I0fde6c63-6277-4c75-a042-7c5e\
30636ddd\x01\n\x05\x01\x01\x04\x1f\x06G/vtbe197358/vtE\
ventPolicy1684328524\x06\x17EventPolic\
y\x01\n\x19\x01\x05\x00\x00\x00\x00\x00\x00\x00\x00\x01\x06^\x01\x01\n\x1d\x05Bq\xcdSo\rp\x00\x06t\
\x06<\x06t\x06t\x068\x06<\x068\x05Bq\xcdSo\rp\x00\x06I82ba6bc0-\
99d6-4240-a856-e61f02836e3c\x01\n\x05\x01\x01\
\x04\x1f\x06?/vtbe197358/vtRelease1539719\
193\x06\x0fRelease\x01\n\x19\x01\x05\x00\x00\x00\x00\x00\x00\x00\x00\x01\x06^\x01\x01\n\x1d\
\x05Bq\xcdSo\x190\x00\x06t\x06\x031\x06t\x06t\x068\x06<\x068\x05Bq\xcdSo\x190\
\x00\x06I79f51d42-2a8b-42ba-ba18-037d5\
a808a00\x01\n\x05\x01\x01\x04\x1f\x06=/vtbe197358/vtSe\
rver1821959325\x06\rServer\x01\n\x19\x01\x05\x00\x00\x00\x00\x00\
\x00\x00\x00\x01\x06^\x01\x01\n\x1d\x05Bq\xcdSogP\x00\x06t\x06\x0516\x06t\x06t\x068\x06\
<\x068\x05Bq\xcdSogP\x00\x06I64405863-5a3f-430c\
-8b7a-09beb360c128\x01\n\x05\x01\x01\x04\x1f\x063/vtbe\
197358/vtRole2552982\x06\tRole\x01\n\x19\x01\x05\x00\
\x00\x00\x00\x00\x00\x00\x00\x01\x06^\x01\x01\n\x1d\x05Bq\xcdSoq \x00\x06r\x06<\x06t\x06r\x06\
8\x06<\x068\x05Bq\xcdSoq \x00\x06I005de7f6-4eb8-45\
3b-91f7-d1a7af2964ac\x01\n\x05\x01\x01\x04\x1f\x06G/vt\
be197358/vtEventSource1770492725\
\x06\x17EventSource\x01\n\x19\x01\x05\x00\x00\x00\x00\x00\x00\x00\x00\x01\x06^\x01\x01\n\
!\x05Bq\xcdSo\x970\x00\x06t\x06\x0528\x06t\x06r\x06<\x068\x068\x05Bq\xcdSo\
\x970\x00\x06 \x06I2ba7662c-ea90-4831-aa46-4\
23efcfbfddd\x01\n\x05\x01\x01\x04\x1f\x06=/vtbe197358/\
vtLayout2025855158\x06\rLayout\x01\n\x19\x01\x05\x00\
\x00\x00\x00\x00\x00\x00\x00\x01\x06^\x01\x01\n\x1d\x05Bq\xcdSo\xa7\xd0\x00\x06r\x06<\x06t\x06r\x06\
8\x06<\x068\x05Bq\xcdSo\xa7\xd0\x00\x06I8a5b5fc7-c838-43\
38-847b-77950985736d\x01\n\x05\x01\x01\x04\x1f\x063/vt\
be197358/vtFeed2185662\x06\tFeed\x01\n\x19\x01\
\x05\x00\x00\x00\x00\x00\x00\x00\x00\x01\x06^\x01\x01\nS\x01`dljp\x05Bq\xcdSx.0\x00\x06\
<\x06<\x068\x05Bq\xcdSx.0\x00\x06I18a35263-d9b7-4f\
cc-b02d-8a0859a55801\x01\n\x05\x01\x01\x04\x1f\x067/vt\
be197358/vtImage70760763\x06\x0bImage\x01\
\x03\n\x15\t\x01\x01\n\x15\t\x03\x01\n\x19\x01\x05\x00\x00\x00\x00\x00\x00\x00\x00\x01\x06'Busine\
ssEnvironment\x01\x01\n3\x01`jp\x05Bq\xcdSn\x1b0\x00\x068\
\x05Bq\xcdSn\x1b0\x00\x06Iaf4ceba2-4af5-44d7-ae\
ed-4c6213d6ae7f\x01\n\x05\x01\x01\x04\x1f\x06\x17/vtbe197\
358\x06 \x01\x03";

def get_data_5():
	return \
"\x00\x03\x00\x00\x00\x03\x00\x0c/21/onResult\x00\x00\xff\xff\xff\xff\x11\n\x81\x03Uf\
lex.messaging.messages.Acknowled\
geMessage\x17destination\x0fheaders\x1bco\
rrelationId\x13messageId\x13timestamp\x11\
clientId\x15timeToLive\tbody\x01\n\x03\x01\x06IFE\
EE411E-CB62-557B-43CA-FF9899AD0E\
6B\x06ICC0391B8-C70A-BF93-9FE3-A930\
6F9A0489\x05Bq\xcf\xf9\x89\xabp\x00\x06ICBF4AA6C-780B\
-A12F-15F4-33C3C5BF062C\x05\x00\x00\x00\x00\x00\x00\x00\x00\
\n\x07Cflex.messaging.io.ArrayCollec\
tion\t\x05\x01\n\t\t\x01\x01\n\t\t\x01\x01\x00\x0c/22/onResult\x00\
\x00\xff\xff\xff\xff\x11\n\x81\x03Uflex.messaging.message\
s.AcknowledgeMessage\x17destination\
\x0fheaders\x1bcorrelationId\x13messageId\
\x13timestamp\x11clientId\x15timeToLive\tb\
ody\x01\n\x03\x01\x06I22A93C75-A8C2-22FA-49D7\
-FF989A1ACA37\x06ICC03922B-8608-AF0\
6-FD25-6261E2D687F5\x05Bq\xcf\xf9\x89\xae`\x00\x06ICB\
F4AA6C-780B-A12F-15F4-33C3C5BF06\
2C\x05\x00\x00\x00\x00\x00\x00\x00\x00\n3Ccom.vitria.m3oui.c\
ore.ListWrapper\ttype\tdata\x0fversio\
n\x06\x07ALL\n\x07Cflex.messaging.io.Array\
Collection\t\x05\x01\n\x82\x037com.vitria.m3ou\
i.core.Model\x11lcStatus\x19lcStatusDa\
te\x15lcStatusBy\x1a\x11lockedBy\x11category\
\x15properties\x05id\x15references\x11conten\
ts\x1bremovedRefers\x19lcStatusNote\x0bfl\
ags\tpath\tname\x19removedProps\x01\x05\x00\x00\x00\x00\
\x00\x00\x00\x00\x01\x06\rFolder\x01\x01\nS\x01\x17vt:lastDate\x19v\
t:firstUser\x17vt:lastUser\x0fvtui:KS\x19\
vt:firstDate\x05Bq\xcd\xaa$Op\x00\x06\x13vtbaadmin\
\x06P\x06\x0fProcess\x05Bq\xcd\xaa$Op\x00\x06I8ef7ecb5-c\
68f-4362-adde-96117ada0bbe\x01\n\x05\x01\x01\x04\
\x02\x06{/vtworkflow35379135/vtProcess\
1355134543/vtResolution393434316\
\x06\x15Resolution\x01\n\x11\x01\x05\x00\x00\x00\x00\x00\x00\x00\x00\x01\x06D\x01\x01\n\x15\
\x05Bq\xcd\xaa$c\xe0\x00\x06P\x06P\x06R\x05Bq\xcd\xaa$c\xe0\x00\x06Ieb7408\
1f-c233-4ee7-9b08-0b25f2ca1c29\x01\n\
\x05\x01\x01\x04\x12\x06}/vtworkflow35379135/vtPro\
cess1355134543/vtSubprocess14623\
24145\x06\x15Subprocess\x01\x04\x00\x00\x0c/23/onResu\
lt\x00\x00\xff\xff\xff\xff\x11\n\x81\x03Uflex.messaging.mess\
ages.AcknowledgeMessage\x17destinat\
ion\x0fheaders\x1bcorrelationId\x13messag\
eId\x13timestamp\x11clientId\x15timeToLiv\
e\tbody\x01\n\x03\x01\x06I42BD44E7-9127-231D-6\
3EE-FF989A1A6E40\x06ICC03930E-930E-\
220A-1599-B861B68248B2\x05Bq\xcf\xf9\x89\xb40\x00\x06\
ICBF4AA6C-780B-A12F-15F4-33C3C5B\
F062C\x05\x00\x00\x00\x00\x00\x00\x00\x00\n3Ccom.vitria.m3ou\
i.core.ListWrapper\ttype\tdata\x0fver\
sion\x06\x07ALL\n\x07Cflex.messaging.io.Ar\
rayCollection\t\x01\x01\x04\x00";

def get_data_6():
	return \
'\x00\x03\x00\x00\x00\x02\x00\x0c/44/onResult\x00\x00\xff\xff\xff\xff\x11\n\x81\x03Uf\
lex.messaging.messages.Acknowled\
geMessage\x17destination\x0fheaders\x1bco\
rrelationId\x13messageId\x13timestamp\x11\
clientId\x15timeToLive\tbody\x01\n\x03\x01\x06I3A\
471483-65B8-7EB3-5B52-FF9DBEA2BB\
EE\x06ICC1024F6-C10E-1A4B-2719-9FF6\
2894FCF5\x05Bq\xcf\xf9\xdc\x15\x10\x00\x06ICC10226F-C82A\
-6723-42B9-30D1FB54D53C\x05\x00\x00\x00\x00\x00\x00\x00\x00\
\x06\x99W<?xml version="1.0" encoding=\
"UTF-8"?>\r\n<events>\r\n<event name\
="workflow.task.server.taskcreat\
ion" label="Task Creation">\r\n<ac\
tion name="notifyManager" label=\
"Notify Manager"/>\r\n<action name\
="notifyPerformer" label="Notify\
 Task Performer"/>\r\n<action name\
="setPriority" label="Escalate T\
ask"/>\r\n</event>\r\n<event name="w\
orkflow.activity.server.taskassi\
gnbymanager,workflow.task.server\
.posttaskreassign" label="Task A\
ssignment">\r\n<action name="notif\
yManager" label="Notify Manager"\
/>\r\n<action name="notifyPerforme\
r" label="Notify Task Performer"\
/>\r\n<action name="setPriority" l\
abel="Escalate Task"/>\r\n</event>\
\r\n<event name="workflow.task.ser\
ver.updatedoc" label="Task Updat\
e">\r\n<action name="notifyManager\
" label="Notify Manager"/>\r\n<act\
ion name="notifyPerformer" label\
="Notify Task Performer"/>\r\n<act\
ion name="setPriority" label="Es\
calate Task"/>\r\n</event>\r\n<event\
 name="workflow.task.server.sett\
asknotes" label="Add Note">\r\n<ac\
tion name="notifyManager" label=\
"Notify Manager"/>\r\n<action name\
="notifyPerformer" label="Notify\
 Task Performer"/>\r\n<action name\
="setPriority" label="Escalate T\
ask"/>\r\n</event>\r\n<event name="w\
orkflow.task.server.taskcompleti\
on,workflow.task.server.taskclos\
ing" label="Task Closed">\r\n<acti\
on name="notifyManager" label="N\
otify Manager"/>\r\n<action name="\
notifyPerformer" label="Notify T\
ask Performer"/>\r\n<action name="\
setPriority" label="Escalate Tas\
k"/>\r\n</event>\r\n<event name="wor\
kflow.task.server.resume" label=\
"Task Resume">\r\n<action name="no\
tifyManager" label="Notify Manag\
er"/>\r\n<action name="notifyPerfo\
rmer" label="Notify Task Perform\
er"/>\r\n<action name="setPriority\
" label="Escalate Task"/>\r\n</eve\
nt>\r\n</events>\x00\x0c/45/onResult\x00\x00\xff\xff\
\xff\xff\x11\n\x81\x03Uflex.messaging.messages.A\
cknowledgeMessage\x17destination\x0fhe\
aders\x1bcorrelationId\x13messageId\x13ti\
mestamp\x11clientId\x15timeToLive\tbody\
\x01\n\x03\x01\x06IC877BBBE-5490-023A-A52B-FF\
9DC10343AA\x06ICC10251D-D10F-D09B-4\
C23-7133604765C3\x05Bq\xcf\xf9\xdc\x16\x10\x00\x06ICBF4A\
A6C-780B-A12F-15F4-33C3C5BF062C\x05\
\x00\x00\x00\x00\x00\x00\x00\x00\n3Ccom.vitria.m3oui.core\
.ListWrapper\ttype\tdata\x0fversion\x06\x07\
ALL\n\x07Cflex.messaging.io.ArrayCol\
lection\t\x0b\x01\n\x82\x037com.vitria.m3oui.c\
ore.Model\x11lcStatus\x19lcStatusDate\x15\
lcStatusBy\x1a\x11lockedBy\x11category\x15pr\
operties\x05id\x15references\x11contents\x1b\
removedRefers\x19lcStatusNote\x0bflags\
\tpath\tname\x19removedProps\x01\x05\x00\x00\x00\x00\x00\x00\x00\
\x00\x01\x06\rFolder\x01\x01\nc\x01\x17vt:lastDate\x19vt:f\
irstUser\x17vt:lastUser\x0fvtui:KS\x19vt:\
firstDate\x0fvtui:BE\x05Bq\xcd\xaa%\xb2\xb0\x00\x06\x13vtba\
admin\x06R\x06\rSchema\x05Bq\xcd\xaa%\xb2\xb0\x00\x06\x11workfl\
ow\x06Icef11c11-0b97-4de0-b92e-c41f\
6c098b82\x01\n\x05\x01\x01\x04\x10\x06{/vtworkflow3537\
9135/vtSchema1824120383/vtConstr\
aint1803088381\x06\x15Constraint\x01\n\x11\x01\x05\x00\
\x00\x00\x00\x00\x00\x00\x00\x01\x06D\x01\x01\n\x15\x05Bq\xcd\xaa/\xd5\xf0\x00\x06R\x06R\x06T\x05Bq\
\xcd\xaa/\xd5\xf0\x00\x06V\x06I514f5a43-ca43-4a49-a3b\
2-08fc6d8667fc\x01\n\x05\x01\x01\x04\x10\x06u/vtworkfl\
ow35379135/vtSchema1824120383/vt\
DBSchema831433793\x06\x11DBSchema\x01\n\x11\x01\x05\
\x00\x00\x00\x00\x00\x00\x00\x00\x01\x06D\x01\x01\n\x15\x05Bq\xcd\xaa%\xd3\xe0\x00\x06R\x06R\x06T\x05B\
q\xcd\xaa%\xd3\xe0\x00\x06V\x06Ib63c002a-f9d0-402c-aa\
1a-77b0a2923a81\x01\n\x05\x01\x01\x04\x10\x06u/vtworkf\
low35379135/vtSchema1824120383/v\
tDocument926364987\x06\x11Document\x01\n\x11\x01\
\x05\x00\x00\x00\x00\x00\x00\x00\x00\x01\x06D\x01\x01\n\x15\x05Bq\xcd\xaa,\xf7\x00\x00\x06R\x06R\x06T\x05\
Bq\xcd\xaa,\xf7\x00\x00\x06V\x06I2f7407b4-b100-4361-9\
786-f4bf832d3975\x01\n\x05\x01\x01\x04\x10\x06m/vtwork\
flow35379135/vtSchema1824120383/\
vtEvent67338874\x06\x0bEvent\x01\n\x11\x01\x05\x00\x00\x00\x00\x00\
\x00\x00\x00\x01\x06D\x01\x01\n\x15\x05Bq\xcd\xaa/\xc1p\x00\x06R\x06R\x06T\x05Bq\xcd\xaa/\xc1\
p\x00\x06V\x06I06beb778-d1f4-4d5f-aa11-ad\
d9552b917b\x01\n\x05\x01\x01\x04\x10\x06i/vtworkflow35\
379135/vtSchema1824120383/vtTask\
2599333\x06\tTask\x01\x04\x01';

def get_data_7():
	return \
'\x00\x03\x00\x00\x00\x02\x00\r/104/onResult\x00\x00\xff\xff\xff\xff\x11\n\x81\x03U\
flex.messaging.messages.Acknowle\
dgeMessage\x17destination\x0fheaders\x1bc\
orrelationId\x13messageId\x13timestamp\
\x11clientId\x15timeToLive\tbody\x01\n\x03\x01\x06I9\
D69A2B8-62A8-D883-C5A1-FFBD95042\
8C3\x06ICC5DDDDF-2708-2A40-E373-371\
7995AD576\x05Bq\xcf\xfb\xd9qp\x00\x06ICC5CDDEA-402\
A-CB67-8C32-5D41C1D9810F\x05\x00\x00\x00\x00\x00\x00\x00\
\x00\n#\x01chttp://schema.vitria.com/mo\
del/TaskHeader:XSDTYPEuhttp://sa\
mples.vitria.com/OrderFulfillmen\
t/Payment:XSDTYPE\nCKcom.vitria.m\
3oui.schema.NSComplexType\x17comple\
xType\x13isBuildIn\x1fpersistencetype\x0b\
qname\x06\x92#<xs:complexType xmlns:xs\
="http://www.w3.org/2001/XMLSche\
ma" xmlns:ecore="http://www.ecli\
pse.org/emf/2002/Ecore" xmlns:tn\
s="http://schema.vitria.com/mode\
l" name="TaskHeader" targetNames\
pace="http://schema.vitria.com/m\
odel">\r\n    <xs:sequence>\r\n    <\
xs:element maxOccurs="1" minOccu\
rs="1" name="id" type="xs:string\
"/>\r\n    <xs:element maxOccurs="\
1" minOccurs="1" name="businessE\
nvironment" type="xs:string"/>\r\n\
    <xs:element maxOccurs="1" mi\
nOccurs="1" name="caseID" type="\
xs:string"/>\r\n    <xs:element ma\
xOccurs="1" minOccurs="1" name="\
activity" type="xs:string"/>\r\n  \
  <xs:element maxOccurs="1" minO\
ccurs="1" name="performer" type=\
"xs:string"/>\r\n    <xs:element m\
axOccurs="1" minOccurs="1" name=\
"description" type="xs:string"/>\
\r\n    <xs:element maxOccurs="1" \
minOccurs="1" name="priority" ty\
pe="xs:int"/>\r\n    <xs:element m\
axOccurs="1" minOccurs="0" name=\
"state" type="xs:string"/>\r\n    \
<xs:element maxOccurs="1" minOcc\
urs="1" name="endReason" type="x\
s:string"/>\r\n    <xs:element max\
Occurs="1" minOccurs="0" name="d\
ueDate" type="xs:dateTime"/>\r\n  \
  <xs:element maxOccurs="1" minO\
ccurs="0" name="createTime" type\
="xs:dateTime"/>\r\n    </xs:seque\
nce>\r\n  </xs:complexType>\x02\x06\x07LOB\x06\
Shttp://schema.vitria.com/model/\
TaskHeader\n\r\x06\x88[<xsd:complexType \
xmlns:xsd="http://www.w3.org/200\
1/XMLSchema" xmlns="http://sampl\
es.vitria.com/OrderFulfillment" \
xmlns:tns="http://samples.vitria\
.com/OrderFulfillment" name="Pay\
ment" targetNamespace="http://sa\
mples.vitria.com/OrderFulfillmen\
t">\r\n        <xsd:sequence>\r\n   \
         <xsd:element name="orde\
rID" type="xsd:string"/>\r\n      \
      <xsd:element name="method"\
 type="xsd:string"/>\r\n          \
  <xsd:element name="option" typ\
e="xsd:string"/>\r\n            <x\
sd:element name="amount" type="x\
sd:float"/>\r\n        </xsd:seque\
nce>\r\n    </xsd:complexType>\x02\x06(\x06\
ehttp://samples.vitria.com/Order\
Fulfillment/Payment\x00\r/105/onResu\
lt\x00\x00\xff\xff\xff\xff\x11\n\x81\x03Uflex.messaging.mess\
ages.AcknowledgeMessage\x17destinat\
ion\x0fheaders\x1bcorrelationId\x13messag\
eId\x13timestamp\x11clientId\x15timeToLiv\
e\tbody\x01\n\x03\x01\x06I785C19CB-E5AA-9720-2\
CE1-FFBD9504561B\x06ICC5DE08D-300F-\
33E5-F0E3-D5EACEEBB59D\x05Bq\xcf\xfb\xd9\x83\x00\x00\x06\
ICC5CEEE1-831E-EE85-6870-B6D514B\
D74F2\x05\x00\x00\x00\x00\x00\x00\x00\x00\n\x07Cflex.messaging.\
io.ArrayCollection\t-\x01\nS3com.vitr\
ia.m3oui.sum.User\x0bphone\risUser\x0be\
mail\tname\x05id\x01\x03\x01\x01\x06\rwf0011\n\r\x01\x03\x01\x01\x06\r\
wf0016\n\r\x01\x03\x01\x01\x06\rwf0000\n\r\x01\x03\x01\x06+Vitri\
a BA system user\x06\x15vtbasystem\n\r\x01\x03\
\x01\x01\x06\rwf0010\n\r\x01\x03\x01\x01\x06\rwf0014\n\r\x01\x03\x01\x01\x06\r\
wf0019\n\r\x01\x03\x01\x01\x06\rwf0012\n\r\x01\x03\x01\x01\x06\rwf00\
04\n\r\x01\x03\x01\x01\x06\rwf0015\n\r\x01\x03\x01\x01\x06\rwf0006\n\r\
\x01\x03\x01\x01\x06\rwf0017\n\r\x01\x03\x01\x01\x06\rwf0003\n\r\x01\x03\x01\x01\
\x06\rwf0018\n\r\x01\x03\x01\x01\x06\rwf0007\n\r\x01\x03\x01\x06/Vit\
ria BA administrator\x06\x13vtbaadmin\n\
\r\x01\x03\x01\x01\x06\rwf0002\n\r\x01\x03\x01\x01\x06\rwf0001\n\r\x01\x03\x01\
\x01\x06\rwf0005\n\r\x01\x03\x01\x01\x06\rwf0013\n\r\x01\x03\x01\x01\x06\rw\
f0009\n\r\x01\x03\x01\x01\x06\rwf0008';


def get_data_8():
	return \
"\x00\x03\x00\x00\x00\x01\x00\x0b/5/onResult\x00\x00\xff\xff\xff\xff\x11\n\x81\x03Ufl\
ex.messaging.messages.Acknowledg\
eMessage\x17destination\x0fheaders\x1bcor\
relationId\x13messageId\x13timestamp\x11c\
lientId\x15timeToLive\tbody\x01\n\x03\x01\x06I2B3\
E2367-B662-133E-D612-005FD693E8F\
C\x06ICDE9FB98-E00C-EE23-1111-6E968\
3D729AC\x05Bq\xd0\x05\xfdn\x00\x00\x06ICDE9FB01-8209-\
96A0-FACD-F282BF63ADB2\x05\x00\x00\x00\x00\x00\x00\x00\x00\n\
\x07Cflex.messaging.io.ArrayCollect\
ion\t\x03\x01\nCUcom.vitria.m3oui.calend\
ar.BusinessCalendar\rconfig!paren\
tCalendarId\x05id\x15resourceId\nsScom.\
vitria.m3oui.calendar.BCConfigur\
ation\x11holidays#workingDayEndDate\
'workingDayStartDate\x0fweekend\tnam\
e\x15timezoneId\x19overtimeDays\n\t\t\x01\x01\x08\x01\
A~\xe6(\x00\x00\x00\x00\x08\x01\x00\x00\x00\x00\x00\x00\x00\x00\n\t\t\x05\x01\x04\x01\x04\x07\x06\x01\x063(\
GMT+08:00) Asia/Shanghai\n\t\t\x01\x01\x04\x00\x04\
\x01\x06\x0fDefault";

# }}}

def get_data_from_file(path):
	fp = open(path, 'rb')
	bytes = fp.read()
	fp.close()
	return bytes

##################################################

class TestSample(unittest.TestCase):
	def setUp(self):
		self.samples = [
				get_data_1(),
				get_data_2(),
				get_data_3(),
				get_data_4(),
				get_data_5(),
				#get_data_6(),
				#get_data_7(),
				get_data_8(),
				get_data_from_file('samples/9.txt'),
				get_data_from_file('samples/10.txt'),
				get_data_from_file('samples/11.txt'),
				get_data_from_file('samples/12.txt'),
				get_data_from_file('samples/13.txt'),
				]

		# data that contains \r can't be handled very well
		self.samples2 = [
				get_data_6(),
				get_data_7(),
				]
	def assertRawPacketEqual(self, r1, r2):
		self.assertEqual(len(r1), len(r2))

	def runEncoderDecoder(self, sample):
		decoder = AMFDecoder(sample)
		packet = decoder.decode()
		encoder = AMFEncoder(packet)
		result = encoder.encode()

		self.assertRawPacketEqual(sample, result)

	def runEncoderDecoder2(self, sample):
		decoder = AMFDecoder(sample)
		packet = decoder.decode()
		encoder = AMFEncoder(packet)
		sample2 = encoder.encode()

		decoder = AMFDecoder(sample2)
		packet = decoder.decode()
		encoder = AMFEncoder(packet)
		sample3 = encoder.encode()
		self.assertEqual(sample2, sample3)

	def runEncoderDecoderXML(self, sample):
		decoder = AMFDecoder(sample)
		packet = decoder.decode()
		toxml = ToXML(packet)
		xml = toxml.get_xml()
		fromxml = FromXML(xml)
		new_packet = fromxml.get_packet()
		encoder = AMFEncoder(new_packet)
		result = encoder.encode()

		self.assertRawPacketEqual(sample, result)

	def runEncoderDecoderXML2(self, sample):
		decoder = AMFDecoder(sample)
		packet = decoder.decode()
		toxml = ToXML(packet)
		xml = toxml.get_xml()
		fromxml = FromXML(xml)
		new_packet = fromxml.get_packet()
		encoder = AMFEncoder(new_packet)
		sample2 = encoder.encode()

		decoder = AMFDecoder(sample2)
		packet = decoder.decode()
		toxml = ToXML(packet)
		xml = toxml.get_xml()
		fromxml = FromXML(xml)
		new_packet = fromxml.get_packet()
		encoder = AMFEncoder(new_packet)
		sample3 = encoder.encode()

		self.assertEqual(sample2, sample3)

	def testAllByEncoderDecoder(self):
		for sample in self.samples:
			self.runEncoderDecoder(sample)
			self.runEncoderDecoder2(sample)

	def testAllWithXML(self):
		for sample in self.samples:
			self.runEncoderDecoderXML(sample)
			self.runEncoderDecoderXML2(sample)

	def test2AllByEncoderDecoder(self):
		for sample in self.samples2:
			#self.runEncoderDecoder(sample)
			self.runEncoderDecoder2(sample)

	def test2AllWithXML(self):
		for sample in self.samples2:
			#self.runEncoderDecoderXML(sample)
			self.runEncoderDecoderXML2(sample)

##################################################

if __name__ == '__main__':
	unittest.main()


# vim: foldmethod=marker:
