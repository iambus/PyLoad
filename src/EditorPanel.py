
import wx
import wx.lib.layoutf

from editor.CodeCtrl import CodeCtrl

from Binding import *

import Logger
log = Logger.getLogger()

def GenerateTempFilePath(content = None):
	#TODO: use a better approach...
	import tempfile
	import os
	fd, path = tempfile.mkstemp(suffix = '.txt', prefix = 'pyload-')
	fp = os.fdopen(fd, 'wb')
	if content:
		fp.write(content)
	fp.close()
	return path

def GetFont():
	fontAttrs = [10, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Courier New']
	return wx.Font(*fontAttrs)

class EditorPanel(wx.Panel):
	def __init__(self, parent, binding = None, filepath = None):
		wx.Panel.__init__(self, parent, -1)

		self.binding = binding
		self.path = filepath
		self.temppath = None

		self.editor = CodeCtrl(self, -1,
                       size=(200, 100), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
		self.viButton = wx.Button(self, -1, 'Edit in Vim')
		self.saveButton = wx.Button(self, -1, 'Save')
		searchLabel = wx.StaticText(self, -1, "Search: ", style=wx.ALIGN_CENTRE)
		self.searchField = wx.TextCtrl(self, -1, style=wx.TE_PROCESS_ENTER)
		self.searchButton = wx.Button(self, -1, 'Search')
		self.reCheck = wx.CheckBox(self, -1, "Regular Expression")

		self.font = GetFont()
		self.editor.SetFont(self.font)


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
		assert self.temppath == None
		if self.path:
			path = self.path
		else:
			self.temppath = GenerateTempFilePath(self.editor.GetValue())
			path = self.temppath
		assert self.path != None or self.temppath != None
		assert path != None
		cmd = 'gvim -b '+path
		self.process = wx.Process(self)
		pid = wx.Execute(cmd, wx.EXEC_ASYNC, self.process)

	def OnViEnded(self, event):
		assert self.path == None or self.temppath == None
		assert self.path != None or self.temppath != None
		path = self.path or self.temppath
		self.temppath = None

		fp = open(path, 'rb')
		try:
			v = fp.read()
		finally:
			fp.close()

		self.editor.SetValue(v)
		if self.binding:
			self.binding.set(v)

		self.process.Destroy()

	def OnSave(self, event):
		self.Save()

	def OnSearch(self, event):
		print 'search'

	def Load(self, path = None):
		assert self.path == None or self.temppath == None
		#FIXME: order is not correct
		if path:
			self.path = path
		if self.binding:
			self.editor.SetValue(self.binding.get())
		elif self.path:
			fp = open(self.path, 'rb')
			self.editor.SetValue(fp.read())
			fp.close()
		elif self.temppath:
			fp = open(self.temppath, 'rb')
			self.editor.SetValue(fp.read())
			fp.close()

	def Save(self):
		assert self.temppath == None
		if self.binding:
			self.binding.set(self.editor.GetValue())
		if self.path:
			fp = open(self.path, 'wb')
			fp.write(self.editor.GetValue())
			fp.close()

	def BindTo(self, variable, name):
		self.binding = AttrBinding(variable, name)
		# please use Load explicitly
		#self.editor.SetValue(self.binding.get())

	def BindToFuncs(self, readfunc, writefunc):
		self.binding = FuncBinding(readfunc, writefunc)
		# please use Load explicitly
		#self.editor.SetValue(self.binding.get())


if __name__ == '__main__':

	app = wx.PySimpleApp()
	#app.RedirectStdio()

	frame = wx.Frame(None, -1, "Editor", size = (800, 600))
	#EditorPanel(frame, 'F:/temp/_')
	EditorPanel(frame)

	frame.Center()
	frame.Show(True)
	app.MainLoop()

