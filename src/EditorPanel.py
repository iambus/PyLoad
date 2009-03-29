
import wx

from editor.CodeCtrl import CodeCtrl
from editor.SearchBar import SearchBar

from Changes import make_change, remove_change

from Binding import *

import Logger
log = Logger.getLogger()

##################################################

# {{{ Function Editors
def WriteToConsole(text):
	print text

# FIXME: duplicated code in Main.py
def SaveToFile(parent, text):
	wildcard = "Text (*.txt)|*.txt|"     \
			   "All files (*.*)|*.*"
	dialog = wx.FileDialog(
			parent, message="Save file as ...", defaultDir="",
			defaultFile="", wildcard=wildcard, style=wx.SAVE
			)
	dialog.SetFilterIndex(0)
	if dialog.ShowModal() == wx.ID_OK:
		path = dialog.GetPath()
	dialog.Destroy()
	if not path:
		return

	# Give a warning if file exists
	import os.path
	if os.path.exists(path):
		dialog = wx.MessageDialog(parent, '%s exists. Do you want to overwrite it?' % path,
				'Save Confirmation',
				wx.YES_NO | wx.ICON_WARNING
				)
		selection = dialog.ShowModal()
		dialog.Destroy()
		if selection != wx.ID_YES:
			return

	fp = open(path, 'w')
	try:
		fp.write(text)
	finally:
		fp.close()

# FIXME: duplicated code in Main.py
def OpenFile(parent, ignore):
	wildcard = "text (*.txt)|*.txt|"     \
			   "All files (*.*)|*.*"
	dialog = wx.FileDialog(
			parent, message="Open File", defaultDir="",
			defaultFile="", wildcard=wildcard, style=wx.OPEN
			)
	dialog.SetFilterIndex(0)
	if dialog.ShowModal() == wx.ID_OK:
		path = dialog.GetPath()
	dialog.Destroy()
	if path:
		fp = open(path, 'r')
		try:
			return fp.read()
		finally:
			fp.close()

from XMLViewer import FindAndShowXML
# }}}

EDITORS = [
		('Vim', 'gvim -b %s'),
		('Emacs', 'emacs %s'),
		('', ''),
		('Print to Console', WriteToConsole),
		('Save As...', SaveToFile),
		('Open', OpenFile),
		('',''),
		('View XML', FindAndShowXML),
]

##################################################
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

##################################################
class EditorPanel(wx.Panel):
	def __init__(self, parent, binding = None, filepath = None):
		wx.Panel.__init__(self, parent, -1)

		self.binding = binding
		self.path = filepath
		self.temppath = None
		self.lock = False

		self.editor = CodeCtrl(self, -1,
                       size=(200, 100), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)

		self.viButton = wx.Button(self, -1, 'Edit in Vim')

		self.saveButton = wx.Button(self, -1, 'Apply')
		self.saveButton.Disable()

		self.search = SearchBar(self)
		self.search.searchCallback = self.editor.SearchText
		self.search.highlightCallback = self.editor.HighlightText
		self.search.cancelSearchCallback = self.editor.CancelSearch


		self.InitMenu()

		# bindings
		self.editor.UsePopUp(False)
		self.editor.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

		self.Bind(wx.stc.EVT_STC_CHANGE, self.OnModified, self.editor)

		self.Bind(wx.EVT_BUTTON, self.OnVi, self.viButton)
		self.Bind(wx.EVT_BUTTON, self.OnSave, self.saveButton)
		#self.Bind(wx.EVT_BUTTON, self.OnSearch, self.searchButton)
		#self.Bind(wx.EVT_TEXT_ENTER, self.OnSearch, self.searchField)

		self.Bind(wx.EVT_END_PROCESS, self.OnEditEnded)

		# layout
		bsizer = wx.FlexGridSizer(cols=6, hgap=10, vgap=10)
		#bsizer.AddGrowableCol(3)
		bsizer.Add(self.viButton, 0, wx.ALL)
		bsizer.Add(self.saveButton, 0, wx.ALL)

		bsizer.Add(self.search, 0, wx.ALL)


		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.Add(self.editor, 1, wx.EXPAND)
		vsizer.Add(bsizer, 0, wx.ALL, 5)

		self.SetSizer(vsizer)

		if self.path:
			self.Load()

	# {{{ Menu
	def InitMenu(self):
		menu = wx.Menu()
		self.menu = menu

		self.ID_UNDO      = wx.NewId()
		self.ID_REDO      = wx.NewId()
		self.ID_CUT       = wx.NewId()
		self.ID_COPY      = wx.NewId()
		self.ID_PASTE     = wx.NewId()
		self.ID_DELETE    = wx.NewId()
		self.ID_SELECTALL = wx.NewId()

		menu.Append(self.ID_UNDO,       "Undo")
		menu.Append(self.ID_REDO,       "Redo")
		menu.AppendSeparator()
		menu.Append(self.ID_CUT,        "Cut")
		menu.Append(self.ID_COPY,       "Copy")
		menu.Append(self.ID_PASTE,      "Paste")
		menu.Append(self.ID_DELETE,     "Delete")
		menu.AppendSeparator()
		menu.Append(self.ID_SELECTALL, "Select All")

		self.Bind(wx.EVT_MENU, lambda e: self.editor.Undo(), id = self.ID_UNDO)
		self.Bind(wx.EVT_MENU, lambda e: self.editor.Redo(), id = self.ID_REDO)
		self.Bind(wx.EVT_MENU, lambda e: self.editor.Cut(), id = self.ID_CUT)
		self.Bind(wx.EVT_MENU, lambda e: self.editor.Copy(), id = self.ID_COPY)
		self.Bind(wx.EVT_MENU, lambda e: self.editor.Paste(), id = self.ID_PASTE)
		self.Bind(wx.EVT_MENU, lambda e: self.editor.Clear(), id = self.ID_DELETE)
		self.Bind(wx.EVT_MENU, lambda e: self.editor.SelectAll(), id = self.ID_SELECTALL)

		self.extEditors = []
		if EDITORS:
			menu.AppendSeparator()
			#editMenu = wx.Menu()
			#menu.AppendMenu(-1, "Edit with...", editMenu)
			editMenu = menu
			def Handler(editor):
				if callable(editor):
					return lambda e: self.EditByFunc(editor)
				else:
					return lambda e: self.EditWith(editor)
			for label, editor in EDITORS:
				if label:
					id = wx.NewId()
					editMenu.Append(id, label)
					callback = Handler(editor)
					self.Bind(wx.EVT_MENU, callback, id = id)
					self.extEditors.append((id, editor))
				else:
					editMenu.AppendSeparator()

	def UpdateMenu(self):
		selection = self.editor.GetSelection()
		hasSelectedSomething = selection[0] != selection[1]
		self.menu.Enable(self.ID_UNDO, self.editor.CanUndo())
		self.menu.Enable(self.ID_REDO, self.editor.CanRedo())
		self.menu.Enable(self.ID_CUT, hasSelectedSomething)
		self.menu.Enable(self.ID_COPY, hasSelectedSomething)
		self.menu.Enable(self.ID_PASTE, self.editor.CanPaste())
		self.menu.Enable(self.ID_DELETE, hasSelectedSomething)

	def OnContextMenu(self, event):
		self.UpdateMenu()
		self.PopupMenu(self.menu)
	# }}}

	# {{{ External Editors
	def LockEditor(self):
		assert not self.lock, "Locked by others"
		self.lock = True
		for id, editor in self.extEditors:
			if not callable(editor):
				self.menu.Enable(id, False)
		self.viButton.Enable(False)

	def UnlockEditor(self):
		assert self.lock, "Not locked yet!"
		self.lock = True
		for id, editor in self.extEditors:
			if not callable(editor):
				self.menu.Enable(id, True)
		self.viButton.Enable(True)

	def EditByFunc(self, func):
		text = self.editor.GetValue()
		try:
			text = func(text)
		except TypeError:
			text = func(self, text)
		if isinstance(text, basestring):
			self.editor.SetValue(text)

	def EditWith(self, editor):
		assert self.temppath == None
		if self.path:
			path = self.path
		else:
			self.temppath = GenerateTempFilePath(self.editor.GetValue())
			path = self.temppath
		assert self.path != None or self.temppath != None
		assert path != None
		cmd = editor % path
		self.process = wx.Process(self)
		pid = wx.Execute(cmd, wx.EXEC_ASYNC, self.process)
		if pid:
			self.LockEditor()
		else:
			# can't find program
			self.temppath = None
			self.process.Destroy()

	def OnEditEnded(self, event):
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
		#if self.binding:
		#	self.binding.set(v)

		self.process.Destroy()

		self.UnlockEditor()

	def OnVi(self, event):
		self.EditWith('gvim -b %s')
	# }}}

	def OnModified(self, event):
		#FIXME: how to clear the Modify status?
		if self.binding or self.path:
			self.saveButton.Enable()
	
	@make_change
	def OnSave(self, event):
		self.Save()
		self.saveButton.Disable()

	def OnSearch(self, event):
		raise NotImplementedError()


	def Unload(self):
		self.binding = None
		self.path = None
		self.temppath = None
		self.saveButton.Disable()

		self.editor.EmptyUndoBuffer()

		self.editor.SetValue('')


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

		self.saveButton.Disable()

		self.editor.EmptyUndoBuffer()
		self.editor.SetSavePoint()

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

	def GetValue(self):
		return self.editor.GetValue()
	
	def SetValue(self, text):
		self.editor.SetValue(text)


##################################################

if __name__ == '__main__':

	app = wx.PySimpleApp()
	#app.RedirectStdio()

	frame = wx.Frame(None, -1, "Editor", size = (800, 600))
	#EditorPanel(frame, 'F:/temp/_')
	p = EditorPanel(frame)

	frame.Center()
	frame.Show(True)
	app.MainLoop()


# vim: foldmethod=marker:
