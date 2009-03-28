
import wx


# TODO: support "highlight all"
class SearchBar(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1)

		self.searchField = wx.SearchCtrl(self, -1, size=(200,-1), style=wx.TE_PROCESS_ENTER)
		self.searchField.ShowSearchButton(True)
		self.searchField.ShowCancelButton(True)
		self.InitHistory()

		iconSize = (16, 16)
		#self.downButton = wx.Button(self, -1, 'Next')
		downIcon = wx.ArtProvider_GetBitmap(wx.ART_GO_DOWN, wx.ART_OTHER, iconSize)
		self.downButton = wx.BitmapButton(self, -1, downIcon, iconSize, (26, 26))
		self.downButton.SetToolTipString("Next")
		#self.upButton = wx.Button(self, -1, 'Prev')
		upIcon = wx.ArtProvider_GetBitmap(wx.ART_GO_UP, wx.ART_OTHER, iconSize)
		self.upButton = wx.BitmapButton(self, -1, upIcon, iconSize, (26, 26))
		self.upButton.SetToolTipString("Prvious")

		self.caseCheck = wx.CheckBox(self, -1, "Match Case")
		self.caseCheck.SetToolTipString("Match Case")
		self.reCheck = wx.CheckBox(self, -1, "RE")
		self.reCheck.SetToolTipString("Use Regular Expression")

		sizer = wx.FlexGridSizer(cols=5, hgap=4, vgap=10)
		sizer.AddGrowableCol(4)
		sizer.Add(self.searchField, 1, wx.EXPAND)
		sizer.Add(self.downButton, 2, wx.ALIGN_CENTER_VERTICAL)
		sizer.Add(self.upButton, 3, wx.ALIGN_CENTER_VERTICAL)
		sizer.Add(self.caseCheck, 4, wx.ALIGN_CENTER_VERTICAL)
		sizer.Add(self.reCheck, 5, wx.ALIGN_CENTER_VERTICAL)

		self.SetSizer(sizer)

		# bindings
		#self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch, self.searchField)
		self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel, self.searchField)
		self.Bind(wx.EVT_TEXT_ENTER, self.OnEnterSearch, self.searchField)
		self.Bind(wx.EVT_TEXT, self.OnIncrSearch, self.searchField)        

		self.Bind(wx.EVT_MENU, self.OnHistory)
 
		self.Bind(wx.EVT_BUTTON, self.OnNext, self.downButton)
		self.Bind(wx.EVT_BUTTON, self.OnPrev, self.upButton)


		#
		self.searchCallback = None
		self.highlightCallback = None
		self.cancelSearchCallback = None

	def OnNext(self, event):
		self.Next()

	def OnPrev(self, event):
		self.Prev()

	def OnSearch(self, event):
		self.Search()
	
	def OnEnterSearch(self, event):
		self.Search()
	
	def OnIncrSearch(self, event):
		# do incremental search only when 'regular expression' is not used
		if not self.IsReChecked():
			# Don't add incr search keyword to history
			if self.searchCallback:
				self.searchCallback(self.GetSearchText(), True, self.matchCase(), self.IsReChecked())

	def OnHistory(self, event):
		itemID = event.GetId()
		item = self.menu.FindItemById(itemID)
		if item != None:
			self.searchField.SetValue(item.GetLabel())
		else:
			event.Skip()

	
	def OnCancel(self, event):
		pass

	def OnHighlight(self, event):
		self.Highlight()

	def matchCase(self):
		return self.caseCheck.IsChecked()

	def IsReChecked(self):
		return self.reCheck.IsChecked()

	def GetSearchText(self):
		return self.searchField.GetValue() 

	def Search(self):
		self.Next()

	def Next(self):
		keyword = self.GetSearchText()
		self.AddSearchHistory(keyword)
		if self.searchCallback:
			self.searchCallback(keyword, True, self.matchCase(), self.IsReChecked())

	def Prev(self):
		keyword = self.GetSearchText()
		self.AddSearchHistory(keyword)
		if self.searchCallback:
			self.searchCallback(keyword, False, self.matchCase(), self.IsReChecked())

	def InitHistory(self):
		self.history = []
		self.maxHistory = 10
		menu = wx.Menu()
		labelMenu = menu.Append(-1, "Recent Search")
		labelMenu.Enable(False)
		menu.AppendSeparator()
		self.searchField.SetMenu(menu)
		self.menu = menu

	def AddSearchHistory(self, keyword):
		if not keyword:
			return
		for item in self.menu.GetMenuItems():
			if keyword == item.GetLabel():
				self.menu.RemoveItem(item)

		item = wx.MenuItem(self.menu, wx.NewId(), keyword)
		self.menu.InsertItem(2, item)

		self.history.insert(0, keyword)
		if len(self.history) > self.maxHistory:
			self.history.pop()

		if self.menu.GetMenuItemCount() > self.maxHistory:
			self.menu.RemoveItem(list(self.menu.GetMenuItems())[-1])

	def GetSearchHistory(self, keywords):
		self.history = []
		self.history.extend(keywords)
		map(self.menu.RemoveItem, list(self.menu.GetMenuItems())[2:])
		if len(keywords) > self.maxHistory:
			keywords = keywords[-self.maxHistory:]
		for keyword in keywords:
			item = wx.MenuItem(self.menu, wx.NewId(), keyword)
			self.menu.AppendItem(item)

	def GetSearchHistory(self):
		return self.history

	def CancelSearch(self, event):
		if self.cancelSearchCallback:
			self.cancelSearchCallback()

	def Highlight(self):
		if self.highlightCallback:
			self.highlightCallback(self.GetSearchText())


if __name__ == '__main__':

	app = wx.PySimpleApp()
	#app.RedirectStdio()

	frame = wx.Frame(None, -1, "Editor", size = (800, 600))
	sb = SearchBar(frame)
	sb.GetSearchHistory(['a', 'b', 'c'])

	frame.Center()
	frame.Show(True)
	app.MainLoop()

# vim: foldmethod=marker:
