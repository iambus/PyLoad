
import wx
import wx.lib.newevent

import InfoPanel
import EditorPanel

from DetailsPanel import DetailsPanel

import Record

import Logger
log = Logger.getLogger()

class ColoredPanel(wx.Window):
	def __init__(self, parent, color = 'red'):
		wx.Window.__init__(self, parent, -1, style = wx.SIMPLE_BORDER)
		self.SetBackgroundColour(color)


##################################################
#
##################################################
# {{{ Record Tree
class RecordTree(wx.TreeCtrl):
	def __init__(self, parent):
		wx.TreeCtrl.__init__(self, parent, 
				style =
				wx.TR_DEFAULT_STYLE
				#wx.TR_HAS_BUTTONS
				| wx.TR_EDIT_LABELS
				#| wx.TR_MULTIPLE
				| wx.TR_HIDE_ROOT
				| wx.TR_HAS_VARIABLE_ROW_HEIGHT
				)
	def SelectedData(self):
		return self.GetPyData(self.GetSelection())


from wx.lib.mixins.treemixin import ExpansionState
class wxRecordTree(ExpansionState, wx.TreeCtrl):
	def __init__(self, parent):
		wx.TreeCtrl.__init__(self, parent,
				style =
				wx.TR_DEFAULT_STYLE
				#wx.TR_HAS_BUTTONS
				| wx.TR_EDIT_LABELS
				#| wx.TR_MULTIPLE
				| wx.TR_HIDE_ROOT
				| wx.TR_HAS_VARIABLE_ROW_HEIGHT
				)


		def AppendItem(self, parent, text, image=-1, wnd=None):
			item = wx.TreeCtrl.AppendItem(self, parent, text, image=image)
		return item

	def GetItemIdentity(self, item):
		return self.GetPyData(item)
# }}}

##################################################
# {{{ Record Panel
(HitEvent, EVT_HIT_UPDATED) = wx.lib.newevent.NewEvent()
class RecordPanel(wx.Panel):
	def __init__(self, parent):
		# Use the WANTS_CHARS style so the panel doesn't eat the Return key.
		wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)


		self.Bind(wx.EVT_SIZE, self.OnSize)

		self.splitter = wx.SplitterWindow(self, style=wx.BORDER_NONE)

		self.InitializeRoot()
		self.detailPanel = DetailsPanel(self.splitter)

		self.splitter.SetMinimumPaneSize(20)
		self.splitter.SplitVertically(self.tree, self.detailPanel, 180)


		sizer = wx.BoxSizer()
		sizer.Add(self.splitter, proportion=1, flag=wx.EXPAND)
		self.SetSizer(sizer) 

		# Event Binding
		self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self.tree)
		self.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.OnBeginEdit, self.tree)
		self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnEndEdit, self.tree)

		self.tree.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClick)
		self.tree.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
		self.tree.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)

		self.Bind(EVT_HIT_UPDATED, self.OnHit)

		self.Bind(wx.EVT_BUTTON, self.OnPlay, self.detailPanel.testButton)

	########################################

	def InitializeRoot(self):
		self.tree = RecordTree(self.splitter)

		iconSize = (16,16)
		iconList = wx.ImageList(iconSize[0], iconSize[1])
		self.recordIcon     = iconList.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, iconSize))
		self.recordOpenIcon = iconList.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER_OPEN, wx.ART_OTHER, iconSize))
		self.pageIcon       = iconList.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, iconSize))
		self.pageOpenIcon   = iconList.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER_OPEN, wx.ART_OTHER, iconSize))
		self.actionIcon     = iconList.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, iconSize))

		self.tree.SetImageList(iconList)
		self.iconList = iconList
		self.root = self.tree.AddRoot("All records")
		self.tree.SetPyData(self.root, None)
		self.tree.SetItemImage(self.root, self.recordIcon, wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(self.root, self.recordOpenIcon, wx.TreeItemIcon_Expanded)



	def ResetSize(self):
		self.splitter.SetSashPosition(170)


	########################################

	def OnRightDown(self, event):
		pt = event.GetPosition();
		item, flags = self.tree.HitTest(pt)
		if item:
			self.tree.SelectItem(item)


	def OnRightUp(self, event):
		pt = event.GetPosition();
		item, flags = self.tree.HitTest(pt)
		if item:        
			self.tree.EditLabel(item)


	def OnBeginEdit(self, event):
		item = event.GetItem()


	def OnEndEdit(self, event):
		item = event.GetItem()
		data = self.tree.GetPyData(item)
		assert type(data.label) == str or type (data.label) == unicode, 'Invalid label type:%s' % type(data.label)
		data.label = event.GetLabel()


	def OnLeftDClick(self, event):
		pt = event.GetPosition();
		item, flags = self.tree.HitTest(pt)
		event.Skip()


	def OnSize(self, event):
		event.Skip()


	def OnSelChanged(self, event):
		self.item = event.GetItem()
		data = self.tree.GetPyData(self.item)
		self.detailPanel.Load(data)
		#event.Skip()


	def OnExit(self):
		self.tree.DeleteAllItems()


	def OnHit(self, event):
		self.AppendHit(event.hit, event.isNewHit)

	def OnPlay(self, event):
		self.Play()

	########################################

	def LastRecord(self):
		assert self.tree.Count, 'There is no record yet!'
		return self.tree.GetLastChild(self.root)

	########################################

	def AppendRecord(self, record):
		assert False, "Don't use it right now"
		recordItem = self.tree.AppendItem(self.root, "%s" % record.label)
		self.tree.SetPyData(recordItem, record)
		self.tree.SetItemImage(recordItem, self.recordIcon, wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(recordItem, self.recordOpenIcon, wx.TreeItemIcon_Expanded)

		for p in record.pages:
			last = self.tree.AppendItem(recordItem, p.path)
			self.tree.SetPyData(last, p)
			self.tree.SetItemImage(last, self.recordIcon, wx.TreeItemIcon_Normal)
			self.tree.SetItemImage(last, self.recordOpenIcon, wx.TreeItemIcon_Expanded)

			for h in p.hits:
				item = self.tree.AppendItem(last, h.label)
				self.tree.SetPyData(item, h)
				self.tree.SetItemImage(item, self.actionIcon, wx.TreeItemIcon_Normal)
				self.tree.SetItemImage(item, self.actionIcon, wx.TreeItemIcon_Selected)
	
	def AppendNewRecord(self, record):
		self.project.add_record(record)
		record.make_folder()

		recordItem = self.tree.AppendItem(self.root, "%s" % record.label)
		self.tree.SetPyData(recordItem, record)
		self.tree.SetItemImage(recordItem, self.recordIcon, wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(recordItem, self.recordOpenIcon, wx.TreeItemIcon_Expanded)


	def AppendHit(self, hit, updated = False):
		if updated:
			self.UpdateHit(hit)
		else:
			self.AppendNewHit(hit)

	def AppendNewHit(self, hit):
		recordItem = self.LastRecord()
		record = self.tree.GetPyData(recordItem)
		if record.add_hit(hit):
			# Page already exits
			pageItem = self.tree.GetLastChild(recordItem)
		else:
			# New page
			page = record.last_page()
			pageItem = self.tree.AppendItem(recordItem, page.path)
			self.tree.SetPyData(pageItem, page)
			self.tree.SetItemImage(pageItem, self.recordIcon, wx.TreeItemIcon_Normal)
			self.tree.SetItemImage(pageItem, self.recordOpenIcon, wx.TreeItemIcon_Expanded)

		hitItem = self.tree.AppendItem(pageItem, hit.label)
		self.tree.SetPyData(hitItem, hit)
		self.tree.SetItemImage(hitItem, self.actionIcon, wx.TreeItemIcon_Normal)

		self.tree.Expand(recordItem)
		self.tree.Expand(pageItem)
		self.tree.Expand(hitItem)

		hit.save()

	def UpdateHit(self, hit):
		assert False, 'Not implemented...'
		print 'TODO: update hit'

	def PostHit(self, hit, updated = False):
		event = HitEvent(hit = hit, isNewHit = updated)
		wx.PostEvent(self, event)

	def Play(self):
		self.tree.SelectedData().play()
	
	########################################

# }}}

##################################################



if __name__ == '__main__':
	app = wx.PySimpleApp()
	#app.RedirectStdio()

	#frame = RecordPanel(None)
	frame = wx.Frame(None, -1, "RecoradPanel", size = (800, 600))
	rp = RecordPanel(frame)
	import Record
	rp.AppendRecord(Record.Record())
	rp.PostHit(Record.Hit('/'))
	rp.PostHit(Record.Hit('/'))
	rp.PostHit(Record.Hit('/m3oui'))


	frame.Center()
	frame.Show(True)
	app.MainLoop()


# vim: foldmethod=marker
