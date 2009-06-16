
import wx
import wx.lib.layoutf

from control.Tabs import Tabs

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
	tab.Unload()
	if hit.reqstr:
		tab.BindToFuncs(hit.get_reqstr, hit.set_reqstr)
		tab.Load()
		tab.editor.SetSyntax(hit.req_handler.syntax)
		tab.search.useGlobalHistory = True

def LoadResponse(tab, hit):
	tab.Unload()
	if hit.respstr:
		tab.BindTo(hit, 'respstr')
		tab.Load()
		tab.editor.SetSyntax(hit.resp_handler.syntax)
		tab.search.useGlobalHistory = True

def LoadScript(tab, variable, name):
	tab.Unload()
	tab.BindTo(variable, name)
	tab.Load()
	import editor.syntax.python
	tab.editor.SetSyntax(editor.syntax.python)
	tab.search.useGlobalHistory = True

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
	Controller.Block : ('Before', 'After',),
	Special.Special : ('Before', 'After'),
	PlayPolicy.Factory : ('Before', 'After'),
		}

# main class

class MyTabs(Tabs):
	def GetTabNames(self, data):
		return ClassToTabs[data.__class__]

	def InitTab(self, tabName, tab, data):
		TabToInitFuncs[tabName](tab, data)

	def CreateTab(self, tabName):
		return TabToPanel[tabName](self)

	def GetTabType(self, tabName):
		return TabToPanel[tabName]

class DetailsPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1)

		self.tabs = MyTabs(self)
		self.testButton = wx.Button(self, -1, "Test")

		# Layout
		self.SetAutoLayout(True)
		self.tabs.SetConstraints(
				wx.lib.layoutf.Layoutf('t=t10#1;l=l10#1;b_b40#1;r=r10#1',(self,)))
		self.testButton.SetConstraints(
				wx.lib.layoutf.Layoutf('t_10#2;l=l10#1;h*;w*',(self,self.tabs)))
		self.testButton.Hide()


	def Load(self, data, update = False):
		self.Freeze()
		try:
			if data == None:
				# possible on Linux
				# TODO: auto-select next node on Linux when a node is deleted (of course not here)
				self.Unload()
				return

			if update:
				self.UpdateInfo(data)
			else:
				self.tabs.Load(data)
				self.testButton.Show()
		finally:
			self.Thaw()

	def ReLoad(self, data):
		self.tabs.ReLoad(data)
		self.testButton.Show()

	def Unload(self):
		self.tabs.Unload()
		self.testButton.Hide()

	def UpdateInfo(self, data):
		tabName = self.tabs.GetPageText(0)
		assert tabName == 'Info'
		tab = self.tabs.GetPage(0)
		tab.Load(data)


if __name__ == '__main__':
	import Test
	import Record
	r = Record.Record()
	Test.TestPanel(DetailsPanel, lambda p:p.Load(r))


