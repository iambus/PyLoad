
import wx
import wx.lib.newevent
import Record
from Tree import Tree
from FlyFrame import fly
from Changes import make_change, remove_change
import Search


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

		self.panel.MoveData(item, self.data.GetData().split())

		return d  
# }}}

# {{{ RecordPanel
(HitEvent, EVT_HIT_UPDATED) = wx.lib.newevent.NewEvent()
class RecordPanel(wx.Panel):

	# {{{ init
	def __init__(self, parent, isMirror = False):
		wx.Panel.__init__(self, parent, -1)

		self.InitializeRoot()
		
#		# layout
#		import Layout
#		Layout.SingleLayout(self, self.tree)


		self.search = wx.SearchCtrl(self, -1, style=wx.TE_PROCESS_ENTER)
		self.search.ShowSearchButton(True)
		self.search.ShowCancelButton(True)

		self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch, self.search)
		self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel, self.search)
		self.Bind(wx.EVT_TEXT_ENTER, self.OnSearch, self.search)
		self.Bind(wx.EVT_TEXT, self.OnIncrSearch, self.search)        


		box = wx.BoxSizer(wx.VERTICAL)
		box.Add(self.tree, 1, wx.EXPAND)
		box.Add(wx.StaticText(self, label = "Search in tree"), 0, wx.TOP|wx.LEFT, 5)
		box.Add(self.search, 0, wx.EXPAND|wx.ALL, 5)
		self.SetSizer(box)



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
		self.tree = Tree(self, multiple = True)

		iconSize = self.tree.iconSize
		icons = {
			Record.Record : (wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, iconSize),
			                 wx.ArtProvider_GetBitmap(wx.ART_FOLDER_OPEN, wx.ART_OTHER, iconSize)),
			Record.Page   : (wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, iconSize),
			                 wx.ArtProvider_GetBitmap(wx.ART_FOLDER_OPEN, wx.ART_OTHER, iconSize)),
			Record.Hit    :  wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, iconSize), 
				}

		self.tree.SetIcons(icons)
		self.root = self.tree.root


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
		# TODO: if unselected
		item = event.GetItem()
		if item:
			if self.onSelChangedCallback:
				all = self.tree.GetAllSelected()
				if len(all) == 1:
					item = all[0]
					data = self.tree.GetPyData(item)
					self.onSelChangedCallback(data)
				else:
					self.onSelChangedCallback(None)

	def OnRightDown(self, event):
		item = self.GetItemByPosition(event.GetPosition())
		if item and not self.tree.IsSelected(item):
			self.tree.UnselectAll()
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
		self.NotifyObservers(('c', data))


	def OnBeginDragMirror(self, event):
		assert self.isMirror
		uuid = ' '.join([data.uuid for data in map(self.tree.GetPyData, self.tree.GetSelectedRoots())])
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
		datas = map(self.tree.GetPyData, self.tree.GetAllSelected())
		if not datas:
			return event.Veto()
		if len(datas) > 1:
			kind = datas[0].__class__
			if not all(map(lambda d: d.__class__ == kind, datas[1:])):
				return event.Veto()

		uuid = ' '.join([data.uuid for data in datas])
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

		recordItem = self.tree.GetSelected()
		record = self.tree.GetPyData(recordItem)
		if not isinstance(record, Record.Record):
			return

		page = Record.Page('<None>')
		page.label = 'New Page'
		#XXX: pages, or children?
		record.pages.append(page)

		self.tree.AddNode(recordItem, page)
		self.tree.Expand(recordItem)

		self.NotifyObservers(('a', record))

	@make_change
	def OnDeleteItems(self, event):
		items = self.tree.GetSelectedRoots()
		map(self.DeleteItem, items)

	@make_change
	def OnDuplicateItem(self, event):
		oldItem = self.tree.GetSelected()
		oldData = self.tree.GetPyData(oldItem)
		parentItem = self.tree.GetItemParent(oldItem)
		parentData = self.tree.GetPyData(parentItem)

		import Clone
		newData = Clone.clone(oldData)

		#FIXME: duplicated code
		oldData = self.tree.GetPyData(oldItem)
		parentItem = self.tree.GetItemParent(oldItem)

		if parentData:
			children = parentData.children
		else:
			children = self.project.records

		index = children.index(oldData)
		children.insert(index+1, newData)

		self.tree.InsertTree(parentItem, oldItem, newData)

		if parentData:
			self.NotifyObservers(('a', parentData))
		else:
			self.NotifyObservers(('_', None))

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


		items = self.tree.GetSelectedRoots()
		for item in items:
			data = self.tree.GetPyData(item)
			data.set_host(host)
			if self.onSelChangedCallback:
				self.onSelChangedCallback(data, True)


	def OnChangeURL(self, event):
		item = self.tree.GetSelected()
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
		if self.onSelChangedCallback:
			self.onSelChangedCallback(hit, True)


	def OnFly(self, event):
		item = self.tree.GetSelected()
		fly(self, node = item, data = self.tree.GetPyData(item))


	def OnSearch(self, event):
		keyword = self.search.GetValue()
		if keyword:
			func = lambda data: Search.match(keyword, data)
			self.tree.HighlightTree(func)
		else:
			self.tree.UnHighlightTree()

	def OnIncrSearch(self, event):
		self.OnSearch(event)

	def OnCancel(self, event):
		self.tree.UnHighlightTree()

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
			self.Bind(wx.EVT_MENU, self.OnDeleteItems, id=self.popupID3)
			self.Bind(wx.EVT_MENU, self.OnRenameHost, id=self.popupID4)
			self.Bind(wx.EVT_MENU, self.OnChangeURL, id=self.popupID5)
			self.Bind(wx.EVT_MENU, self.OnFly, id=self.popupID6)

		menu = wx.Menu()
		
		nodes = self.tree.GetAllSelected()
		if len(nodes) > 1:
			if not self.isMirror:
				#menu.Append(self.popupID2, "Duplicate")
				menu.Append(self.popupID3, "Delete")
				menu.Append(self.popupID4, "Change Host")
		else:
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

		self.tree.AddNode(self.root, record)

		self.NotifyObservers(('_', None))

	@make_change
	def AppendHit(self, hit, updated = False):
		assert False, "Don't call it now"
		assert not self.isMirror
		if updated:
			# XXX: when this happen?
			self.UpdateHit(hit)
			self.NotifyObservers() # XXX: how to notify?
		else:
			self.AppendNewHit(hit)

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
			pageItem = self.tree.AddNode(recordItem, page)

			self.NotifyObservers(('a', record))

		hitItem = self.tree.AddNode(pageItem, hit)

		self.tree.Expand(recordItem)
		self.tree.Expand(pageItem)
		self.tree.Expand(hitItem)

		self.NotifyObservers(('a', page))

	########################################
	def MoveData(self, targetItem, sourceUUIDs):
		assert not self.isMirror
		sourceUUID = sourceUUIDs[0]
		sourceItem = self.FindItem(sourceUUID)
		sourceData = self.tree.GetPyData(sourceItem)
		targetData = self.tree.GetPyData(targetItem)
		if sourceData == targetData:
			return

		sourceUUIDs = sourceUUIDs[1:]
		if sourceData.__class__ == targetData.__class__:
			sourceUUIDs.reverse()
			for nextUUID in sourceUUIDs:
				self.MoveAfter(self.FindItem(nextUUID), targetItem)
			self.MoveAfter(sourceItem, targetItem)
		elif sourceData.__class__ == Record.Hit and targetData.__class__ == Record.Page:
			self.MoveUnder(sourceItem, targetItem)
			for nextUUID in sourceUUIDs:
				self.MoveUnder(self.FindItem(nextUUID), targetItem)
		elif sourceData.__class__ == Record.Page and targetData.__class__ == Record.Record:
			self.MoveUnder(sourceItem, targetItem)
			for nextUUID in sourceUUIDs:
				self.MoveUnder(self.FindItem(nextUUID), targetItem)
		else:
			return

	def MoveUnder(self, sourceItem, targetItem):
		#TODO: if source is already under target
		sourceData = self.tree.GetPyData(sourceItem)
		targetData = self.tree.GetPyData(targetItem)
		self.DeleteItem(sourceItem)

		targetData.add_child(sourceData)
		self.tree.AddTree(targetItem, sourceData)

		self.NotifyObservers(('a', targetData))

	def MoveAfter(self, sourceItem, targetItem):
		#TODO: if source is already after target
		sourceData = self.tree.GetPyData(sourceItem)
		targetData = self.tree.GetPyData(targetItem)
		parentItem = self.tree.GetItemParent(targetItem)
		parentData = self.tree.GetPyData(parentItem)
		self.DeleteItem(sourceItem)

		if parentData:
			children = parentData.children
		else:
			children = self.project.records

		index = children.index(targetData)
		children.insert(index+1, sourceData)

		self.tree.InsertTree(parentItem, targetItem, sourceData)
		if parentData:
			self.NotifyObservers(('a', parentData))
		else:
			self.NotifyObservers(('_', parentData))

	#FIXME: name confliction?
	@make_change
	def DeleteItem(self, item):
		data = self.tree.GetPyData(item)
		parentItem = self.tree.GetItemParent(item)
		parentData = self.tree.GetPyData(parentItem)
		if parentItem != self.root and self.tree.GetChildrenCount(parentItem, recursively = False) == 1:
			self.tree.Collapse(parentItem)
		self.tree.Delete(item)
		if parentData:
			parentData.remove_child(data)
			self.NotifyObservers(('d', parentData))
		else:
			# parent is root
			assert parentItem == self.root
			self.project.remove_record(data)
			self.NotifyObservers(('_', None))

	########################################

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

	def NotifyObservers(self, *changes):
		if not self.isMirror:
			for m in self.mirrors:
				# TODO: don't reload everything...
				m.LoadAllRecords()
			for callback in self.observers:
				callback(changes)

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
		self.tree.AddTree(self.root, record)
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

# {{{ main
if __name__ == '__main__':
	import Record
	import Project
	def init(p):
		p.project = Project.NoneProject()
		p.AppendNewRecord(Record.Record())
		p.AppendNewRecord(Record.Record())
	import Test
	Test.TestPanel(RecordPanel, init)
# }}}

# vim: foldmethod=marker:
