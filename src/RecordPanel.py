
import wx
import wx.lib.newevent

class SimpleTree(wx.TreeCtrl):
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


(HitEvent, EVT_HIT_UPDATED) = wx.lib.newevent.NewEvent()
class RecordPanel(wx.Panel):
	def __init__(self, parent, isMirror = False):
		wx.Panel.__init__(self, parent, -1)

		self.InitializeRoot()
		
		# layout
		import Layout
		Layout.SingleLayout(self, self.tree)

		self.isMirror = isMirror
		self.mirrors = set()
		self.one = None
		if isMirror:
			self.InitMirror()
		else:
			self.InitSelf()

	########################################

	def InitializeRoot(self):
		self.tree = SimpleTree(self)

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


	def InitSelf(self):
		# Event Binding
		self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self.tree)
		self.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.OnBeginEdit, self.tree)
		self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnEndEdit, self.tree)

		self.tree.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClick)
		self.tree.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
		self.tree.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)

		self.Bind(EVT_HIT_UPDATED, self.OnHit)

		self.onSelChangedCallback = None

	def InitMirror(self):
		self.tree.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnBeginDrag)

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

	def OnBeginDrag(self, event):
		assert self.isMirror
		item = event.GetItem()
		tree = event.GetEventObject()
		uuid = tree.GetPyData(item).uuid
		def DoDragDrop():
			dd = wx.CustomDataObject("xxx")
			dd.SetData(uuid)

			data = wx.DataObjectComposite()
			data.Add(dd)

			dropSource = wx.DropSource(self)
			dropSource.SetData(data)
			result = dropSource.DoDragDrop(wx.Drag_AllowMove)

		wx.CallAfter(DoDragDrop) # can't call dropSource.DoDragDrop here..

	def OnSelChanged(self, event):
		self.item = event.GetItem()
		data = self.tree.GetPyData(self.item)
		if self.onSelChangedCallback:
			self.onSelChangedCallback(data)

	def OnSize(self, event):
		event.Skip()

	def OnExit(self):
		self.tree.DeleteAllItems()


	def OnHit(self, event):
		self.AppendHit(event.hit, event.isNewHit)

	########################################

	def LastRecord(self):
		assert self.tree.Count, 'There is no record yet!'
		return self.tree.GetLastChild(self.root)

	########################################

	def AppendNewRecord(self, record):
		assert not self.isMirror
		self.project.add_record(record)
		record.make_folder()

		recordItem = self.tree.AppendItem(self.root, "%s" % record.label)
		self.tree.SetPyData(recordItem, record)
		self.tree.SetItemImage(recordItem, self.recordIcon, wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(recordItem, self.recordOpenIcon, wx.TreeItemIcon_Expanded)

		self.NotifyMirrors()

	def AppendHit(self, hit, updated = False):
		assert False, "Don't call it now"
		assert not self.isMirror
		if updated:
			self.UpdateHit(hit)
		else:
			self.AppendNewHit(hit)
		self.NotifyMirrors()

	def AppendNewHit(self, hit):
		assert not self.isMirror
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
		self.NotifyMirrors()

	########################################

	def SetMirrorOf(self, one):
		assert one.__class__ == RecordPanel
		self.one = one
		self.one.mirrors.add(self)

	def NotifyMirrors(self):
		if not self.isMirror:
			for m in self.mirrors:
				m.LoadAllRecords()

	def LoadAllRecords(self):
		assert self.isMirror
		self.tree.DeleteChildren(self.root)

		project = self.one.project
		for r in project.records:
			self.AppendRecord(r)

	def AppendRecord(self, record):
		assert self.isMirror
		recordItem = self.tree.AppendItem(self.root, "%s" % record.label)
		self.tree.SetPyData(recordItem, record)
		self.tree.SetItemImage(recordItem, self.recordIcon, wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(recordItem, self.recordOpenIcon, wx.TreeItemIcon_Expanded)

		for p in record.pages:
			pageItem = self.tree.AppendItem(recordItem, p.path)
			self.tree.SetPyData(pageItem, p)
			self.tree.SetItemImage(pageItem, self.recordIcon, wx.TreeItemIcon_Normal)
			self.tree.SetItemImage(pageItem, self.recordOpenIcon, wx.TreeItemIcon_Expanded)

			for h in p.hits:
				hitItem = self.tree.AppendItem(pageItem, h.label)
				self.tree.SetPyData(hitItem, h)
				self.tree.SetItemImage(hitItem, self.actionIcon, wx.TreeItemIcon_Normal)
				self.tree.SetItemImage(hitItem, self.actionIcon, wx.TreeItemIcon_Selected)

				self.tree.Expand(hitItem)

			self.tree.Expand(pageItem)

		self.tree.Expand(recordItem)

	########################################
	def UpdateHit(self, hit):
		assert False, 'Not implemented...'
		print 'TODO: update hit'

	def PostHit(self, hit, updated = False):
		event = HitEvent(hit = hit, isNewHit = updated)
		wx.PostEvent(self, event)

	########################################
	def Play(self):
		self.tree.SelectedData().play()



if __name__ == '__main__':
	import Record
	import Project
	def init(p):
		p.project = Project.NoneProject()
		p.AppendNewRecord(Record.Record())
	import Test
	Test.TestPanel(RecordPanel, init)


