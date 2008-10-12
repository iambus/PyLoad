
import wx

class PlainSearchBar(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1)


		self.xButton = wx.Button(self, -1, 'X')
		searchLabel = wx.StaticText(self, -1, "Search: ", pos=(10, 20), style=wx.ALIGN_CENTRE)
		self.searchField = wx.TextCtrl(self, -1, style=wx.TE_PROCESS_ENTER)
		self.searchButton = wx.Button(self, -1, 'Search')
		self.previousButton = wx.Button(self, -1, 'Previous')
		self.nextButton = wx.Button(self, -1, 'Next')
		self.reCheck = wx.CheckBox(self, -1, "Regular Expression")

		sizer = wx.FlexGridSizer(cols=7, hgap=10, vgap=10)
		sizer.AddGrowableCol(2)
		sizer.Add(self.xButton, 0, wx.ALL)
		sizer.Add(searchLabel, 0, wx.ALL)
		sizer.Add(self.searchField, 1, wx.EXPAND)
		sizer.Add(self.searchButton, 0, wx.ALL)
		sizer.Add(self.previousButton, 0, wx.ALL)
		sizer.Add(self.nextButton, 0, wx.ALL)
		sizer.Add(self.reCheck, 0, wx.ALL)

		self.SetSizer(sizer)


# TODO: enable tab
class SimpleSearchBar(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1)

		self.searchField = wx.SearchCtrl(self, -1, size=(200,-1), style=wx.TE_PROCESS_ENTER)
		self.searchField.ShowSearchButton(True)
		self.searchField.ShowCancelButton(True)
		self.searchField.SetMenu(self.MakeMenu())

		sizer = wx.FlexGridSizer(cols=7, hgap=10, vgap=10)
		sizer.AddGrowableCol(2)
		sizer.Add(self.searchField, 1, wx.EXPAND)

		self.SetSizer(sizer)

		# bindings
		self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch, self.searchField)
		self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel, self.searchField)
		self.Bind(wx.EVT_TEXT_ENTER, self.OnEnterSearch, self.searchField)
		self.Bind(wx.EVT_TEXT, self.OnIncrSearch, self.searchField)        


		#
		self.searchCallback = None
		self.highlightCallback = None
		self.cancelSearchCallback = None


	def MakeMenu(self):
		menu = wx.Menu()
		self.forwardItem = menu.Append(-1, "Forward", kind = wx.ITEM_RADIO)
		self.backwordItem = menu.Append(-1, "Backword", kind = wx.ITEM_RADIO)
		self.reItem = menu.Append(-1, "Regular Expression", kind = wx.ITEM_CHECK)
		#self.hightlightItem = menu.Append(-1, "Highlight All", kind = wx.ITEM_CHECK)
		self.highlightItem = menu.Append(-1, "Highlight All")
		self.Bind(wx.EVT_MENU, self.OnHighlight, self.highlightItem)
		return menu
	
	def OnEvent(self, event):
		print event

	def OnSearch(self, event):
		self.Search()
	
	def OnEnterSearch(self, event):
		self.Search()
	
	def OnIncrSearch(self, event):
		# do incremental search only when 'regular expression' is not used
		if not self.IsReChecked():
			self.Search()
	
	def OnCancel(self, event):
		pass

	def OnHighlight(self, event):
		self.Highlight()

	def IsReChecked(self):
		return self.reItem.IsChecked()

	def IsNext(self):
		return self.forwardItem.IsChecked()

	def GetSearchText(self):
		return self.searchField.GetValue() 

	def Search(self):
		if self.searchCallback:
			self.searchCallback(self.GetSearchText(), self.IsNext(), self.IsReChecked())

	def Highlight(self):
		if self.highlightCallback:
			self.highlightCallback(self.GetSearchText())

	def CancelSearch(self, event):
		if self.cancelSearchCallback:
			self.cancelSearchCallback()


SearchBar = SimpleSearchBar

if __name__ == '__main__':

	app = wx.PySimpleApp()
	#app.RedirectStdio()

	frame = wx.Frame(None, -1, "Editor", size = (800, 600))
	SearchBar(frame)

	frame.Center()
	frame.Show(True)
	app.MainLoop()
