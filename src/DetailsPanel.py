
import wx
import wx.lib.layoutf

from InfoPanel import InfoPanel
from EditorPanel import EditorPanel

import Player
import Record
import Controller
import Special

import PlayPolicy

# mappings

TabToPanel = {
	'Info' : InfoPanel,
	'Before' : EditorPanel,
	'After' : EditorPanel,
	'Request' : EditorPanel,
	'Response' : EditorPanel,
	'Script' : EditorPanel,
	'Condition' : EditorPanel,
		}

def LoadRequest(tab, hit):
	if hit.reqstr:
		tab.Unload()
		tab.BindToFuncs(hit.get_reqstr, hit.set_reqstr)
		tab.Load()
		tab.editor.SetSyntax(hit.req_handler.syntax)

def LoadResponse(tab, hit):
	if hit.respstr:
		tab.Unload()
		tab.BindTo(hit, 'respstr')
		tab.Load()
		tab.editor.SetSyntax(hit.resp_handler.syntax)

def LoadScript(tab, variable, name):
	tab.Unload()
	tab.BindTo(variable, name)
	tab.Load()
	import editor.syntax.python
	tab.editor.SetSyntax(editor.syntax.python)

TabToInitFuncs = {
	'Info' : lambda tab, data: tab.Load(data),
	'Before' : lambda tab, data: LoadScript(tab, data.beforescript, 'script'),
	'After' : lambda tab, data: LoadScript(tab, data.afterscript, 'script'),
	'Request' : LoadRequest,
	'Response' : LoadResponse,
	'Script' : lambda tab, data: LoadScript(tab, data, 'script'),
	'Condition' : lambda tab, data: LoadScript(tab, data.condition, 'script'),
		}

ClassToTabs = {
	Record.Record : ('Info', 'Before', 'After',),
	Record.Page : ('Info', 'Before', 'After',),
	Record.Hit : ('Info', 'Before', 'Request', 'Response', 'After',),
	Player.Script : ('Script',),
	Controller.If : ('Before', 'Condition', 'After',),
	Controller.Loop : ('Before', 'Condition', 'After',),
	Special.Special : ('Before', 'After'),
	PlayPolicy.Factory : ('Before', 'After'),
		}

# main class

class DetailsPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1)

		self.nb = wx.Notebook(self, -1)
		self.testButton = wx.Button(self, -1, "Test")

		# Layout
		self.SetAutoLayout(True)
		self.nb.SetConstraints(
				wx.lib.layoutf.Layoutf('t=t10#1;l=l10#1;b%b90#1;r=r10#1',(self,)))
		self.testButton.SetConstraints(
				wx.lib.layoutf.Layoutf('t_10#2;l=l10#1;h*;w*',(self,self.nb)))
		self.testButton.Hide()

		#self.Bind(wx.EVT_BUTTON, self.testButton, self.OnPlay)

	def RemoveAllPages(self):
		self.nb.DeleteAllPages()
	
	def GiveSharedTabs(self, newTabNames):
		'Avoid re-creating the same tabs'
		currentTabNames = []
		for i in range(self.nb.GetPageCount()):
			currentTabNames.append(self.nb.GetPageText(i))
		minlen = min( len(currentTabNames), len(newTabNames) )
		n = 0
		while n < minlen and TabToPanel[currentTabNames[n]] == TabToPanel[newTabNames[n]]:
			n += 1
		if n == 0:
			self.nb.DeleteAllPages()
			return 0
		else:
			for i in range(n, len(currentTabNames)):
				self.nb.DeletePage(n)
			return n

	def Load(self, data):
		'Avoid re-creating the same tabs'
		c = data.__class__
		tabNames = ClassToTabs[c]

		n = self.GiveSharedTabs(tabNames)

		for i in range(n):
			tab = self.nb.GetPage(i)
			tabName = tabNames[i]
			self.nb.SetPageText(i, tabName)
			TabToInitFuncs[tabName](tab, data)

		for i in range(n, len(tabNames)):
			tabName = tabNames[i]
			tab = TabToPanel[tabName](self.nb)
			self.nb.AddPage(tab, tabName)
			TabToInitFuncs[tabName](tab, data)
		self.testButton.Show()

	def ReLoad(self, data):
		'Always create new tabs'
		self.nb.DeleteAllPages()
		c = data.__class__
		tabNames = ClassToTabs[c]
		for tabName in tabNames:
			tab = TabToPanel[tabName](self.nb)
			self.nb.AddPage(tab, tabName)
			TabToInitFuncs[tabName](tab, data)
		self.testButton.Show()

	def Unload(self):
		self.nb.DeleteAllPages()
		self.testButton.Hide()

if __name__ == '__main__':
	import Test
	import Record
	r = Record.Record()
	Test.TestPanel(DetailsPanel, lambda p:p.Load(r))


