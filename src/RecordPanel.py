
import wx
import wx.lib.newevent
import Record
from FlyFrame import fly
from Changes import make_change, remove_change

# {{{ SimpleTree
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
# }}}

# {{{ DropTarget
class MyDropTarget(wx.PyDropTarget):
	def __init__(self, panel):
		wx.PyDropTarget.__init__(self)
		self.panel = panel
		self.tree = self.panel.tree

		self.data = wx.CustomDataObject("record")
		self.SetDataObject(self.data)

	def OnData(self, x, y, d):
		if not self.GetData():
			return d

		item, flags = self.tree.HitTest((x,y))
		if flags & wx.TREE_HITTEST_NOWHERE:
			return d

		self.panel.MoveData(item, self.data.GetData())

		return d  
# }}}

# {{{ RecordPanel
(HitEvent, EVT_HIT_UPDATED) = wx.lib.newevent.NewEvent()
class RecordPanel(wx.Panel):

	# {{{ init
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

		self.observers = set()

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
		# drag and drop
		self.SetDropTarget(MyDropTarget(self))
		self.tree.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnBeginDragSelf)

		# common event Bindings
		self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self.tree)

		self.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.OnBeginEdit, self.tree)
		self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnEndEdit, self.tree)

		#self.tree.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClick)
		self.tree.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
		self.tree.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)

		#self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

		# hit handler
		self.Bind(EVT_HIT_UPDATED, self.OnHit)
		self.onSelChangedCallback = None

	def InitMirror(self):
		# drag
		self.tree.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnBeginDragMirror)
		
		# label edit
		self.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.OnBeginEdit, self.tree)
		self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnEndEdit, self.tree)

		# play on the fly menu
		self.tree.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
		self.tree.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)

		self.is_in_loading = False

	# }}}

	########################################

	# {{{ event handlers
	def OnSelChanged(self, event):
		self.item = event.GetItem()
		data = self.tree.GetPyData(self.item)
		if self.onSelChangedCallback:
			self.onSelChangedCallback(data)

	def OnRightDown(self, event):
		item = self.GetItemByPosition(event.GetPosition())
		if item:
			self.tree.SelectItem(item)

	def OnRightUp(self, event):
		item = self.GetItemByPosition(event.GetPosition())
		if item:
			#self.tree.EditLabel(item)
			self.ShowContextMenu(item)

	def OnLeftDClick(self, event):
		pt = event.GetPosition();
		item, flags = self.tree.HitTest(pt)
		event.Skip()

	#XXX: why it's not working?
	def OnContextMenu(self, event):
		item = self.GetItemByPosition(event.GetPosition())
		if item:
			print 'right menu for item'
			self.ShowContextMenu(item)


	def OnBeginEdit(self, event):
		if self.isMirror:
			event.Veto()

	# TODO: make_change
	def OnEndEdit(self, event):
		if event.EditCancelled:
			return
		item = event.GetItem()
		data = self.tree.GetPyData(item)
		assert type(data.label) == str or type (data.label) == unicode, 'Invalid label type:%s' % type(data.label)
		data.label = event.GetLabel()
		self.NotifyObservers()


	def OnBeginDragMirror(self, event):
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

		#wx.CallAfter(DoDragDrop) # XXX: not working on Linux
		DoDragDrop()

	def OnBeginDragSelf(self, event):
		assert not self.isMirror
		item = event.GetItem()
		tree = event.GetEventObject()
		uuid = tree.GetPyData(item).uuid
		def DoDragDrop():
			dd = wx.CustomDataObject("record")
			dd.SetData(uuid)

			data = wx.DataObjectComposite()
			data.Add(dd)

			dropSource = wx.DropSource(self)
			dropSource.SetData(data)
			result = dropSource.DoDragDrop(wx.Drag_AllowMove)

		#wx.CallAfter(DoDragDrop) # XXX: not working on Linux
		DoDragDrop()

	@make_change
	def OnNewPage(self, event):
		assert not self.isMirror

		recordItem = self.tree.GetSelection()
		record = self.tree.GetPyData(recordItem)
		if not isinstance(record, Record.Record):
			return

		page = Record.Page('<None>')
		page.label = 'New Page'
		#XXX: pages, or childern?
		record.pages.append(page)

		pageItem = self.tree.AppendItem(recordItem, page.label)
		self.tree.SetPyData(pageItem, page)
		self.tree.SetItemImage(pageItem, self.pageIcon, wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(pageItem, self.pageOpenIcon, wx.TreeItemIcon_Expanded)
		self.tree.Expand(recordItem)

		self.NotifyObservers()

	@make_change
	def OnDeleteItem(self, event):
		item = self.tree.GetSelection()
		self.DeleteItem(item)

	@make_change
	def OnDuplicateItem(self, event):
		oldItem = self.tree.GetSelection()
		oldData = self.tree.GetPyData(oldItem)
		parentItem = self.tree.GetItemParent(oldItem)
		parentData = self.tree.GetPyData(parentItem)

		import Clone
		newData = Clone.clone(oldData)

		#FIXME: duplicated code
		oldData = self.tree.GetPyData(oldItem)
		parentItem = self.tree.GetItemParent(oldItem)

		if parentData:
			childern = parentData.childern
		else:
			childern = self.project.records

		index = childern.index(oldData)
		childern.insert(index+1, newData)

		mappings = {
				Record.Record : self.InsertRecord,
				Record.Page : self.InsertPage,
				Record.Hit : self.InsertHit,
				}
		mappings[newData.__class__](parentItem, oldItem, newData)

	def OnSize(self, event):
		event.Skip()

	def OnExit(self):
		self.tree.DeleteAllItems()


	def OnHit(self, event):
		self.AppendHit(event.hit, event.isNewHit)


	def OnRenameHost(self, event):
		dialog = wx.TextEntryDialog(
				self, 'Please enter new host/port for this item:',
				'Change Host')
		#dialog.SetValue('<host>:<port>')
		host = dialog.GetValue() if dialog.ShowModal() == wx.ID_OK else None
		dialog.Destroy()

		if host == None or host == '':
			return

		import re
		if not re.match(r'^(https?://)?[-\w\d.@%~]+(:\d+)?$', host):
			dialog = wx.MessageDialog(self, 'The host/port is not valid. Operation will be ignored.',
								   'Bad host/port',
								   wx.OK | wx.ICON_WARNING
								   #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
								   )
			dialog.ShowModal()
			dialog.Destroy()
			return


		item = self.tree.GetSelection()
		data = self.tree.GetPyData(item)
		data.set_host(host)


	def OnChangeURL(self, event):
		item = self.tree.GetSelection()
		hit = self.tree.GetPyData(item)

		dialog = wx.TextEntryDialog(
				self, 'Please enter new URL for this request:',
				'Change URL')
		dialog.SetValue(hit.url)
		url = dialog.GetValue() if dialog.ShowModal() == wx.ID_OK else None
		dialog.Destroy()

		if url == None or url == '':
			return

		import re
		if re.match(r'^[-\w\d.@%~]+(:\d+)?$', url):
			url = 'http://'+url
		elif re.match(r'^https?://[-\w\d.@%~]+(:\d+)?.*$', url):
			pass
		else:
			dialog = wx.MessageDialog(self, 'The URL is not valid. Operation will be ignored.',
								   'Bad URL',
								   wx.OK | wx.ICON_WARNING
								   )
			dialog.ShowModal()
			dialog.Destroy()
			return


		hit.set_url(url)


	def OnFly(self, event):
		item = self.tree.GetSelection()
		fly(self, node = item, data = self.tree.GetPyData(item))
	# }}}

	########################################

	def GetItemByPosition(self, position):
		item, flags = self.tree.HitTest(position)
		if item:
			return item

	def ShowContextMenu(self, item):
		if not hasattr(self, "popupID1"):
			self.popupID1 = wx.NewId()
			self.popupID2 = wx.NewId()
			self.popupID3 = wx.NewId()
			self.popupID4 = wx.NewId()
			self.popupID5 = wx.NewId()
			self.popupID6 = wx.NewId()
			self.Bind(wx.EVT_MENU, self.OnNewPage, id=self.popupID1)
			self.Bind(wx.EVT_MENU, self.OnDuplicateItem, id=self.popupID2)
			self.Bind(wx.EVT_MENU, self.OnDeleteItem, id=self.popupID3)
			self.Bind(wx.EVT_MENU, self.OnRenameHost, id=self.popupID4)
			self.Bind(wx.EVT_MENU, self.OnChangeURL, id=self.popupID5)
			self.Bind(wx.EVT_MENU, self.OnFly, id=self.popupID6)

		menu = wx.Menu()
		
		if not self.isMirror:
			if isinstance(self.tree.GetPyData(item), Record.Record):
				menu.Append(self.popupID1, "New Page")
			menu.Append(self.popupID2, "Duplicate")
			menu.Append(self.popupID3, "Delete")
			menu.Append(self.popupID4, "Change Host")
			if isinstance(self.tree.GetPyData(item), Record.Hit):
				menu.Append(self.popupID5, "Change URL")
		menu.Append(self.popupID6, "I'm interested...")

		self.PopupMenu(menu)
		menu.Destroy()

	########################################

	def LastRecord(self):
		assert self.tree.Count, 'There is no record yet!'
		return self.tree.GetLastChild(self.root)

	########################################

	@make_change
	def AppendNewRecord(self, record):
		assert not self.isMirror
		self.project.add_record(record)

		recordItem = self.tree.AppendItem(self.root, "%s" % record.label)
		self.tree.SetPyData(recordItem, record)
		self.tree.SetItemImage(recordItem, self.recordIcon, wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(recordItem, self.recordOpenIcon, wx.TreeItemIcon_Expanded)

		self.NotifyObservers()

	@make_change
	def AppendHit(self, hit, updated = False):
		assert False, "Don't call it now"
		assert not self.isMirror
		if updated:
			self.UpdateHit(hit)
		else:
			self.AppendNewHit(hit)
		self.NotifyObservers()

	@make_change
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
			self.tree.SetItemImage(pageItem, self.pageIcon, wx.TreeItemIcon_Normal)
			self.tree.SetItemImage(pageItem, self.pageOpenIcon, wx.TreeItemIcon_Expanded)

		hitItem = self.tree.AppendItem(pageItem, hit.label)
		self.tree.SetPyData(hitItem, hit)
		self.tree.SetItemImage(hitItem, self.actionIcon, wx.TreeItemIcon_Normal)

		self.tree.Expand(recordItem)
		self.tree.Expand(pageItem)
		self.tree.Expand(hitItem)

		self.NotifyObservers()

	########################################
	def MoveData(self, targetItem, sourceUUID):
		assert not self.isMirror
		sourceItem = self.FindItem(sourceUUID)
		sourceData = self.tree.GetPyData(sourceItem)
		targetData = self.tree.GetPyData(targetItem)
		if sourceData == targetData:
			return

		if sourceData.__class__ == targetData.__class__:
			self.MoveAfter(sourceItem, targetItem)
		elif sourceData.__class__ == Record.Hit and targetData.__class__ == Record.Page:
			self.MoveUnder(sourceItem, targetItem)
		elif sourceData.__class__ == Record.Page and targetData.__class__ == Record.Record:
			self.MoveUnder(sourceItem, targetItem)
		else:
			return

		self.NotifyObservers()

	def MoveUnder(self, sourceItem, targetItem):
		#TODO: if source is already under target
		sourceData = self.tree.GetPyData(sourceItem)
		targetData = self.tree.GetPyData(targetItem)
		self.DeleteItem(sourceItem)

		targetData.add_child(sourceData)
		mappings = {
				Record.Record : self.LoadRecord,
				Record.Page : self.LoadPage,
				Record.Hit : self.LoadHit,
				}
		mappings[sourceData.__class__](targetItem, sourceData)

		self.tree.Expand(targetItem)

	def MoveAfter(self, sourceItem, targetItem):
		#TODO: if source is already after target
		sourceData = self.tree.GetPyData(sourceItem)
		targetData = self.tree.GetPyData(targetItem)
		parentItem = self.tree.GetItemParent(targetItem)
		parentData = self.tree.GetPyData(parentItem)
		self.DeleteItem(sourceItem)

		if parentData:
			childern = parentData.childern
		else:
			childern = self.project.records

		index = childern.index(targetData)
		childern.insert(index+1, sourceData)

		mappings = {
				Record.Record : self.InsertRecord,
				Record.Page : self.InsertPage,
				Record.Hit : self.InsertHit,
				}
		mappings[sourceData.__class__](parentItem, targetItem, sourceData)

	#FIXME: name confliction?
	@make_change
	def DeleteItem(self, item):
		data = self.tree.GetPyData(item)
		parentItem = self.tree.GetItemParent(item)
		parentData = self.tree.GetPyData(parentItem)
		self.tree.Delete(item)
		if parentData:
			parentData.remove_child(data)
		else:
			# parent is root
			assert parentItem == self.root
			self.project.remove_record(data)

		self.NotifyObservers()

	########################################
	#FIXME: duplicated code
	def LoadRecord(self, item, r):
		recordItem = self.tree.AppendItem(item, r.label)
		self.tree.SetPyData(recordItem, r)
		self.tree.SetItemImage(recordItem, self.recordIcon, wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(recordItem, self.recordOpenIcon, wx.TreeItemIcon_Expanded)

		for p in r.pages:
			self.LoadPage(recordItem, p)

		self.tree.Expand(recordItem)

	def LoadPage(self, item, p):
		pageItem = self.tree.AppendItem(item, p.label)
		self.tree.SetPyData(pageItem, p)
		self.tree.SetItemImage(pageItem, self.pageIcon, wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(pageItem, self.pageOpenIcon, wx.TreeItemIcon_Expanded)

		for h in p.hits:
			self.LoadHit(pageItem, h)

		self.tree.Expand(pageItem)

	def LoadHit(self, item, h):
		hitItem = self.tree.AppendItem(item, h.label)
		self.tree.SetPyData(hitItem, h)
		self.tree.SetItemImage(hitItem, self.actionIcon, wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(hitItem, self.actionIcon, wx.TreeItemIcon_Selected)

		self.tree.Expand(hitItem)

	def InsertRecord(self, item, prev, r):
		recordItem = self.tree.InsertItem(item, prev, r.label)
		self.tree.SetPyData(recordItem, r)
		self.tree.SetItemImage(recordItem, self.recordIcon, wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(recordItem, self.recordOpenIcon, wx.TreeItemIcon_Expanded)

		for p in r.pages:
			self.LoadPage(recordItem, p)

		self.tree.Expand(recordItem)

	#FIXME: duplicated code
	#FIXME: bad names -- "insert"?
	def InsertPage(self, item, prev, p):
		pageItem = self.tree.InsertItem(item, prev, p.label)
		self.tree.SetPyData(pageItem, p)
		self.tree.SetItemImage(pageItem, self.pageIcon, wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(pageItem, self.pageOpenIcon, wx.TreeItemIcon_Expanded)

		for h in p.hits:
			self.LoadHit(pageItem, h)

		self.tree.Expand(pageItem)

	def InsertHit(self, item, prev, h):
		hitItem = self.tree.InsertItem(item, prev, h.label)
		self.tree.SetPyData(hitItem, h)
		self.tree.SetItemImage(hitItem, self.actionIcon, wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(hitItem, self.actionIcon, wx.TreeItemIcon_Selected)

		self.tree.Expand(hitItem)

	def FindItem(self, uuid):
		return self.FindItemFrom(self.root, uuid)

	def FindItemFrom(self, item, uuid):
		(child, cookie) = self.tree.GetFirstChild(item)
		while child.IsOk():
			# we have a child
			data = self.tree.GetPyData(child)
			if data.uuid == uuid:
				return child
			i = self.FindItemFrom(child, uuid)
			if i:
				return i
			(child, cookie) = self.tree.GetNextChild(item, cookie)

	########################################
	def Unload(self):
		self.tree.DeleteChildren(self.root)

	def Reload(self):
		assert not self.isMirror
		for r in self.project.records:
			self.LoadRecord(r)
		self.NotifyObservers()

	########################################

	# {{{ mirrors and observers
	def AddObserver(self, callback):
		assert not self.isMirror
		self.observers.add(callback)

	def SetMirrorOf(self, one):
		assert self.isMirror
		assert one.__class__ == RecordPanel
		self.one = one
		self.one.mirrors.add(self)

	def NotifyObservers(self):
		if not self.isMirror:
			for m in self.mirrors:
				m.LoadAllRecords()
			for callback in self.observers:
				callback()

	def LoadAllRecords(self):
		assert self.isMirror
		if self.is_in_loading:
			return
		self.is_in_loading = True
		self.tree.DeleteChildren(self.root)

		project = self.one.project
		for r in project.records:
			self.LoadRecord(r)

		self.is_in_loading = False

	def LoadRecord(self, record):
		#assert self.isMirror
		recordItem = self.tree.AppendItem(self.root, "%s" % record.label)
		self.tree.SetPyData(recordItem, record)
		self.tree.SetItemImage(recordItem, self.recordIcon, wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(recordItem, self.recordOpenIcon, wx.TreeItemIcon_Expanded)

		for p in record.pages:
			pageItem = self.tree.AppendItem(recordItem, p.label)
			self.tree.SetPyData(pageItem, p)
			self.tree.SetItemImage(pageItem, self.pageIcon, wx.TreeItemIcon_Normal)
			self.tree.SetItemImage(pageItem, self.pageOpenIcon, wx.TreeItemIcon_Expanded)

			for h in p.hits:
				hitItem = self.tree.AppendItem(pageItem, h.label)
				self.tree.SetPyData(hitItem, h)
				self.tree.SetItemImage(hitItem, self.actionIcon, wx.TreeItemIcon_Normal)
				self.tree.SetItemImage(hitItem, self.actionIcon, wx.TreeItemIcon_Selected)

				self.tree.Expand(hitItem)

			self.tree.Expand(pageItem)

		self.tree.Expand(recordItem)
	# }}}

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

# }}}

if __name__ == '__main__':
	import Record
	import Project
	def init(p):
		p.project = Project.NoneProject()
		p.AppendNewRecord(Record.Record())
		p.AppendNewRecord(Record.Record())
	import Test
	Test.TestPanel(RecordPanel, init)


# vim: foldmethod=marker:
