
import wx
import wx.lib.layoutf

class EditorPanel(wx.Panel):
	def __init__(self, parent, filepath = None):
		wx.Panel.__init__(self, parent, -1)

		self.path = filepath

		self.editor = wx.TextCtrl(self, -1,
                       size=(200, 100), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
		self.viButton = wx.Button(self, -1, 'Edit in Vim')
		self.saveButton = wx.Button(self, -1, 'Save')
		searchLabel = wx.StaticText(self, -1, "Search: ", style=wx.ALIGN_CENTRE)
		self.searchField = wx.TextCtrl(self, -1, style=wx.TE_PROCESS_ENTER)
		self.searchButton = wx.Button(self, -1, 'Search')
		self.reCheck = wx.CheckBox(self, -1, "Regular Expression")

		self.Bind(wx.EVT_BUTTON, self.OnVi, self.viButton)
		self.Bind(wx.EVT_BUTTON, self.OnSave, self.saveButton)
		self.Bind(wx.EVT_BUTTON, self.OnSearch, self.searchButton)
		self.Bind(wx.EVT_TEXT_ENTER, self.OnSearch, self.searchField)

		self.Bind(wx.EVT_END_PROCESS, self.OnViEnded)


		bsizer = wx.FlexGridSizer(cols=6, hgap=10, vgap=10)
		bsizer.AddGrowableCol(3)
		bsizer.Add(self.viButton, 0, wx.ALL)
		bsizer.Add(self.saveButton, 0, wx.ALL)
		bsizer.Add(searchLabel, 0, wx.ALL)
		bsizer.Add(self.searchField, 1, wx.EXPAND)
		bsizer.Add(self.searchButton, 0, wx.ALL)
		bsizer.Add(self.reCheck, 0, wx.ALL)


		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.Add(self.editor, 1, wx.EXPAND)
		vsizer.Add(bsizer, 0, wx.ALL, 5)

		self.SetSizer(vsizer)

		if self.path:
			self.Load()
	
	def OnVi(self, event):
		if not self.path:
			return
		cmd = 'gvim '+self.path
		self.process = wx.Process(self)
		pid = wx.Execute(cmd, wx.EXEC_ASYNC, self.process)

	def OnViEnded(self, event):
		self.process.Destroy()
		self.Load()

	def OnSave(self, event):
		if self.path:
			self.Save()

	def OnSearch(self, event):
		print 'search'

	def Load(self, path = None):
		if path:
			self.path = path
		if not self.path:
			return
		fp = open(self.path, 'rb')
		self.editor.SetValue(fp.read())
		fp.close()

	def Save(self):
		if not self.path:
			return
		fp = open(self.path, 'wb')
		fp.write(self.editor.GetValue())
		fp.close()

if __name__ == '__main__':
	app = wx.PySimpleApp()
	#app.RedirectStdio()

	frame = wx.Frame(None, -1, "Editor", size = (800, 600))
	EditorPanel(frame, 'F:/temp/_')

	frame.Center()
	frame.Show(True)
	app.MainLoop()

