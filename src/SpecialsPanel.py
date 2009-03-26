
import wx
from Special import Special
import Controller
import Player
import Record
from FlyFrame import fly
from Changes import make_change, remove_change

import Logger
log = Logger.getLogger()

# {{{ DropTarget
class MyDropTarget(wx.PyDropTarget):
	def __init__(self, panel):
		wx.PyDropTarget.__init__(self)
		self.panel = panel
		self.tree = self.panel.tree

		self.controllerData = wx.CustomDataObject("xxx")
		self.specialData = wx.CustomDataObject("special")

		self.data = wx.DataObjectComposite()
		self.data.Add(self.controllerData)
		self.data.Add(self.specialData)

		self.SetDataObject(self.data)


	def OnData(self, x, y, d):
		if not self.GetData():
			return d

		item, flags = self.tree.HitTest((x,y))
		if flags & wx.TREE_HITTEST_NOWHERE:
			log.debug('no place to drop')
			return d

		if self.controllerData.GetData():
			data = self.controllerData.GetData()
			self.panel.DropNewData(item, data)
			#XXX: why I have to set it none?
			self.controllerData.SetData('')
		if self.specialData.GetData():
			data = self.specialData.GetData()
			self.panel.MoveData(item, data)
			#XXX: why I have to set it none?
			self.specialData.SetData('')

		return d  
# }}}

# {{{ SpecialsTree
class SpecialsTree(wx.TreeCtrl):
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

class SpecialsPanel(wx.Panel):
	# {{{ init
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1)
		
		self.InitTree()

		# drag and drop
		self.SetDropTarget(MyDropTarget(self))
		self.tree.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnBeginDrag)
	
		# layout
		import Layout
		Layout.SingleLayout(self, self.tree)

		# bindings
		self.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.OnBeginEdit, self.tree)
		self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnEndEdit, self.tree)

		self.tree.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
		self.tree.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
		#self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

		self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self.tree)
		self.onSelChangedCallback = None

		self.onNewSpecialCallback = None

	def InitTree(self):
		self.tree = SpecialsTree(self)

		iconSize = (16,16)
		iconList = wx.ImageList(iconSize[0], iconSize[1])

		self.specialIcon     = iconList.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, iconSize))
		self.specialOpenIcon = iconList.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER_OPEN, wx.ART_OTHER, iconSize))

		self.recordIcon     = iconList.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, iconSize))
		self.recordOpenIcon = iconList.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER_OPEN, wx.ART_OTHER, iconSize))

		self.pageIcon       = iconList.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, iconSize))
		self.pageOpenIcon   = iconList.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER_OPEN, wx.ART_OTHER, iconSize))
		self.hitIcon     = iconList.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, iconSize))

		self.scriptIcon     = iconList.Add(wx.ArtProvider_GetBitmap(wx.ART_NEW, wx.ART_OTHER, iconSize))
		self.ifIcon     = iconList.Add(wx.ArtProvider_GetBitmap(wx.ART_QUESTION,      wx.ART_OTHER, iconSize))
		self.ifOpenIcon = iconList.Add(wx.ArtProvider_GetBitmap(wx.ART_QUESTION, wx.ART_OTHER, iconSize))
		self.loopIcon     = iconList.Add(wx.ArtProvider_GetBitmap(wx.ART_REDO,      wx.ART_OTHER, iconSize))
		self.loopOpenIcon = iconList.Add(wx.ArtProvider_GetBitmap(wx.ART_REDO, wx.ART_OTHER, iconSize))
		self.blockIcon     = iconList.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, iconSize))
		self.blockOpenIcon = iconList.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, iconSize))

		self.tree.SetImageList(iconList)
		self.iconList = iconList
		self.root = self.tree.AddRoot("All Specials")
		self.tree.SetPyData(self.root, None)
		self.tree.SetItemImage(self.root, self.specialIcon, wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(self.root, self.specialOpenIcon, wx.TreeItemIcon_Expanded)
	# }}}

	# {{{ Event Handler
	def OnBeginEdit(self, event):
		item = event.GetItem()
		data = self.tree.GetPyData(item)
		if not (
				isinstance(data, Special) or
				isinstance(data, Controller.Controller) or
				isinstance(data, Player.Script)
				):
			event.Veto()

	# TODO: make_change
	def OnEndEdit(self, event):
		if event.EditCancelled:
			return
		item = event.GetItem()
		data = self.tree.GetPyData(item)
		assert type(data.label) == str or type (data.label) == unicode, 'Invalid label type:%s' % type(data.label)
		data.label = event.GetLabel()
		self.NotifyObserver()

	def OnBeginDrag(self, event):
		item = event.GetItem()
		self.dragging_item = item
		tree = event.GetEventObject()
		uuid = tree.GetPyData(item).uuid
		def DoDragDrop():
			dd = wx.CustomDataObject("special")
			dd.SetData(uuid)

			data = wx.DataObjectComposite()
			data.Add(dd)

			dropSource = wx.DropSource(self)
			dropSource.SetData(data)
			result = dropSource.DoDragDrop(wx.Drag_AllowMove)

		#wx.CallAfter(DoDragDrop) # XXX: not working on Linux
		DoDragDrop()

	def OnSelChanged(self, event):
		item = event.GetItem()
		if item:
			data = self.tree.GetPyData(item)
			if self.onSelChangedCallback:
				self.onSelChangedCallback(data)

	def OnRightDown(self, event):
		item, flags = self.tree.HitTest(event.GetPosition())
		if item:
			self.tree.SelectItem(item)

	def OnRightUp(self, event):
		item, flags = self.tree.HitTest(event.GetPosition())
		if not hasattr(self, "popupID1"):
			self.popupID1 = wx.NewId()
			self.popupID2 = wx.NewId()
			self.popupID3 = wx.NewId()
			self.popupID4 = wx.NewId()
			self.Bind(wx.EVT_MENU, self.OnNewSpecial, id=self.popupID1)
			self.Bind(wx.EVT_MENU, self.OnDeleteItem, id=self.popupID2)
			self.Bind(wx.EVT_MENU, self.OnDuplicateItem, id=self.popupID3)
			self.Bind(wx.EVT_MENU, self.OnFly, id=self.popupID4)

		menu = wx.Menu()
		menu.Append(self.popupID1, "New Special")
		if item:
			if self.UnderModifiable(item):
				if self.IsCloneable(item):
					menu.Append(self.popupID3, "Duplicate")
					#menu.FindItemByPosition(2).Enable(False)
				menu.Append(self.popupID2, "Delete")
			menu.Append(self.popupID4, "I'm interested...")

		self.PopupMenu(menu)
		menu.Destroy()

	def OnContextMenu(self, event):
		raise NotImplementedError("Use OnRightUp instead")

	def OnNewSpecial(self, event):
		self.AppendNewSpecial()
		self.NotifyObserver()

	def OnDeleteItem(self, event):
		item = self.tree.GetSelection()
		if item:
			self.DeleteItem(item)

	def OnDuplicateItem(self, event):
		item = self.tree.GetSelection()
		if item:
			self.DuplicateItem(item)
			
	def OnFly(self, event):
		item = self.tree.GetSelection()
		assert item
		fly(self, node = item, data = self.tree.GetPyData(item))
	# }}}

	# {{{ Add new nodes
	@make_change
	def AppendNewSpecial(self):
		special = Special()
		self.project.add_special(special)
		special.label = 'New Special'
		specialItem = self.tree.AppendItem(self.root, "New Special")
		self.tree.SetPyData(specialItem, special)
		self.tree.SetItemImage(specialItem, self.specialIcon, wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(specialItem, self.specialOpenIcon, wx.TreeItemIcon_Expanded)

		self.tree.SelectItem(specialItem)

	def InsertNewController(self, item, controller):
		itemData = self.tree.GetPyData(item)
		itemData.add_child(controller)

		label = controller.__class__.__name__
		controller.label = label

		self.LoadData(item, controller)

		self.tree.Expand(item)


	def UseData(self, item, data):
		parentdata = self.tree.GetPyData(item)
		parentdata.add_child(data)

		self.LoadData(item, data)

		self.tree.Expand(item)

	def DropNewData(self, targetItem, uuid):
		targetData = self.tree.GetPyData(targetItem)

		#TODO: can we introduce a "subable" interface?
		subable = (Special, Controller.If, Controller.Loop, Controller.Block)
		unsubable = (Record.Record, Record.Page, Record.Hit, Player.Script)

		if targetData.__class__ in subable:
			# insert under
			sourceData = self.GetDataFromUUID(uuid)
			targetData.add_child(sourceData)
			self.LoadData(targetItem, sourceData)
			self.tree.Expand(targetItem)
		else:
			parentItem = self.tree.GetItemParent(targetItem)
			parentData = self.tree.GetPyData(parentItem)
			if parentData.__class__ in subable:
				# insert after
				sourceData = self.GetDataFromUUID(uuid)
				childern = parentData.childern
				index = childern.index(targetData)
				childern.insert(index+1, sourceData)
				self.InsertData(parentItem, targetItem, sourceData)

	def GetDataFromUUID(self, uuid):
		import Repository
		data = Repository.lookup(uuid)
		import inspect
		if inspect.isclass(data):
			data = data()
			label = data.__class__.__name__
			data.label = label
		return data

	# }}}

	# {{{ Moving nodes
	def MoveData(self, targetItem, data):
		sourceItem = self.dragging_item
		self.dragging_item = None
		sourceData = self.tree.GetPyData(sourceItem)
		targetData = self.tree.GetPyData(targetItem)
		if sourceData == targetData:
			return

		sourceParentItem = self.tree.GetItemParent(sourceItem)
		targetParentItem = self.tree.GetItemParent(targetItem)
		sourceParentData = self.tree.GetPyData(sourceParentItem)
		targetParentData = self.tree.GetPyData(targetParentItem)

		p = targetParentItem
		while p != self.root:
			if p == sourceItem:
				# can't move father node under a child node
				return
			p = self.tree.GetItemParent(p)

		#TODO: can we introduce a "subable" interface?
		subable = (Special, Controller.If, Controller.Loop, Controller.Block)
		unsubable = (Record.Record, Record.Page, Record.Hit, Player.Script)

		if sourceParentData.__class__ in unsubable or targetParentData.__class__ in unsubable:
			return

		if sourceData.__class__ == Special:
			if targetData.__class__ == Special:
				self.MoveAfter(sourceItem, targetItem)
			else:
				# You can only move a special after another special
				pass
		elif targetData.__class__ in subable:
			self.MoveUnder(sourceItem, targetItem)
		else:
			self.MoveAfter(sourceItem, targetItem)

		self.NotifyObserver()

	#FIXME: duplicated code
	def MoveUnder(self, sourceItem, targetItem):
		sourceData = self.tree.GetPyData(sourceItem)
		targetData = self.tree.GetPyData(targetItem)
		self.DeleteItem(sourceItem)

		targetData.add_child(sourceData)
		self.LoadData(targetItem, sourceData)

		self.tree.Expand(targetItem)

	#FIXME: duplicated code
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
			childern = self.project.specials

		index = childern.index(targetData)
		childern.insert(index+1, sourceData)

		self.InsertData(parentItem, targetItem, sourceData)

	# }}}

	# {{{ Deleting nodes
	#FIXME: name confliction?
	@make_change
	def DeleteItem(self, item):
		data = self.tree.GetPyData(item)
		parentItem = self.tree.GetItemParent(item)
		parentData = self.tree.GetPyData(parentItem)

		assert self.IsModifiable(parentItem)

		self.tree.Delete(item)
		if parentData:
			parentData.remove_child(data)
		else:
			# parent is root
			assert parentItem == self.root
			self.project.remove_special(data)

		self.NotifyObserver()
	# }}}

	# {{{ Duplicating nodes
	@make_change
	def DuplicateItem(self, oldItem):
		oldData = self.tree.GetPyData(oldItem)
		parentItem = self.tree.GetItemParent(oldItem)
		parentData = self.tree.GetPyData(parentItem)

		import Clone
		newData = Clone.clone_for_special(oldData)
		if not newData:
			# item is not cloneable
			return

		if parentData:
			childern = parentData.childern
		else:
			childern = self.project.specials

		index = childern.index(oldData)
		childern.insert(index+1, newData)

		self.InsertData(parentItem, oldItem, newData)
	# }}}

	# {{{ Load kinds of Data (the data to be loaded should have been added as parent node's child)
	@make_change
	def LoadData(self, item, data):
		mappings = {
				Record.Record : self.LoadRecord,
				Record.Page : self.LoadPage,
				Record.Hit : self.LoadHit,
				Player.Script : self.LoadScript,
				Controller.If : self.LoadIf,
				Controller.Loop : self.LoadLoop,
				Controller.Block : self.LoadBlock,
				}
		mappings[data.__class__](item, data)

	def LoadSpecial(self, item, s):
		specialItem = self.tree.AppendItem(item, s.label)
		self.tree.SetPyData(specialItem, s)
		self.tree.SetItemImage(specialItem, self.specialIcon, wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(specialItem, self.specialOpenIcon, wx.TreeItemIcon_Expanded)

		for c in s.childern:
			self.LoadData(specialItem, c)

		self.tree.Expand(specialItem)

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
		self.tree.SetItemImage(hitItem, self.hitIcon, wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(hitItem, self.hitIcon, wx.TreeItemIcon_Selected)

		self.tree.Expand(hitItem)

	def LoadScript(self, item, scriptData):
		subItem = self.tree.AppendItem(item, scriptData.label)
		self.tree.SetPyData(subItem, scriptData)
		self.tree.SetItemImage(subItem, self.scriptIcon, wx.TreeItemIcon_Normal)
	
	def LoadIf(self, item, ifData):
		subItem = self.tree.AppendItem(item, ifData.label)
		self.tree.SetPyData(subItem, ifData)
		self.tree.SetItemImage(subItem, self.ifIcon, wx.TreeItemIcon_Normal)

		for child in ifData.childern:
			self.LoadData(subItem, child)

		self.tree.Expand(subItem)

	def LoadLoop(self, item, loopData):
		subItem = self.tree.AppendItem(item, loopData.label)
		self.tree.SetPyData(subItem, loopData)
		self.tree.SetItemImage(subItem, self.loopIcon, wx.TreeItemIcon_Normal)

		for child in loopData.childern:
			self.LoadData(subItem, child)

		self.tree.Expand(subItem)

	def LoadBlock(self, item, blockData):
		subItem = self.tree.AppendItem(item, blockData.label)
		self.tree.SetPyData(subItem, blockData)
		self.tree.SetItemImage(subItem, self.blockIcon, wx.TreeItemIcon_Normal)

		for child in blockData.childern:
			self.LoadData(subItem, child)

		self.tree.Expand(subItem)
	# }}}

	# {{{ Insert kinds of Data AFTER a node (the data to be loaded should have been added as parent node's child)
	#FIXME: duplicated code
	#FIXME: bad names -- why "insert" suppose "the data to be loaded should have been added as parent node's child"?
	@make_change
	def InsertData(self, item, prev, data):
		mappings = {
				Record.Record : self.InsertRecord,
				Record.Page : self.InsertPage,
				Record.Hit : self.InsertHit,
				Player.Script : self.InsertScript,
				Controller.If : self.InsertIf,
				Controller.Loop : self.InsertLoop,
				Controller.Block : self.InsertBlock,
				Special : self.InsertSpecial,
				}
		mappings[data.__class__](item, prev, data)

	def InsertSpecial(self, item, prev, s):
		assert item == self.root
		specialItem = self.tree.InsertItem(item, prev, s.label)
		self.tree.SetPyData(specialItem, s)
		self.tree.SetItemImage(specialItem, self.specialIcon, wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(specialItem, self.specialOpenIcon, wx.TreeItemIcon_Expanded)

		for child in s.childern:
			self.LoadData(specialItem, child)

		self.tree.Expand(specialItem)

	def InsertRecord(self, item, prev, r):
		recordItem = self.tree.InsertItem(item, prev, r.label)
		self.tree.SetPyData(recordItem, r)
		self.tree.SetItemImage(recordItem, self.recordIcon, wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(recordItem, self.recordOpenIcon, wx.TreeItemIcon_Expanded)

		for p in r.pages:
			self.LoadPage(recordItem, p)

		self.tree.Expand(recordItem)

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
		self.tree.SetItemImage(hitItem, self.hitIcon, wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(hitItem, self.hitIcon, wx.TreeItemIcon_Selected)

		self.tree.Expand(hitItem)

	def InsertScript(self, item, prev, scriptData):
		subItem = self.tree.InsertItem(item, prev, scriptData.label)
		self.tree.SetPyData(subItem, scriptData)
		self.tree.SetItemImage(subItem, self.scriptIcon, wx.TreeItemIcon_Normal)
	
	def InsertIf(self, item, prev, ifData):
		subItem = self.tree.InsertItem(item, prev, ifData.label)
		self.tree.SetPyData(subItem, ifData)
		self.tree.SetItemImage(subItem, self.ifIcon, wx.TreeItemIcon_Normal)

		for child in ifData.childern:
			self.LoadData(subItem, child)

		self.tree.Expand(subItem)

	def InsertLoop(self, item, prev, loopData):
		subItem = self.tree.InsertItem(item, prev, loopData.label)
		self.tree.SetPyData(subItem, loopData)
		self.tree.SetItemImage(subItem, self.loopIcon, wx.TreeItemIcon_Normal)

		for child in loopData.childern:
			self.LoadData(subItem, child)

		self.tree.Expand(subItem)

	def InsertBlock(self, item, prev, blockData):
		subItem = self.tree.InsertItem(item, prev, blockData.label)
		self.tree.SetPyData(subItem, blockData)
		self.tree.SetItemImage(subItem, self.blockIcon, wx.TreeItemIcon_Normal)

		for child in blockData.childern:
			self.LoadData(subItem, child)

		self.tree.Expand(subItem)
	# }}}

	##################################################

	def Unload(self):
		self.tree.DeleteChildren(self.root)

	def Reload(self):
		for special in self.project.specials:
			self.LoadSpecial(self.root, special)
		self.NotifyObserver()

	def UpdateSpecial(self, specialNode):
		special = self.tree.GetPyData(specialNode)
		self.tree.DeleteChildren(specialNode)
		for child in special.childern:
			self.LoadData(specialNode, child)

	def UpdateAll(self):
		(child, cookie) = self.tree.GetFirstChild(self.root)
		while child.IsOk():
			self.UpdateSpecial(child)
			(child, cookie) = self.tree.GetNextChild(self.root, cookie)

	def WalkTree(self, node, func):
		stop = func(node)
		if stop:
			return stop
		(child, cookie) = self.tree.GetFirstChild(node)
		while child.IsOk():
			self.WalkTree(child, func)
			(child, cookie) = self.tree.GetNextChild(self.root, cookie)

	def UpdateOne(self, kind, data):
		def CheckNode(node):
			nodeData = self.tree.GetPyData(node)
			if nodeData is data:
				if kind == 'c':
					self.tree.SetItemText(node, data.label)
				elif kind == 'd':
					self.tree.DeleteChildren(node)
					for child in data.childern:
						self.LoadData(node, child)
					return True
				elif kind == 'a':
					self.tree.DeleteChildren(node)
					for child in data.childern:
						self.LoadData(node, child)
					return True
				elif kind == '_':
					# ignore
					pass
				else:
					raise RuntimeError("Unkown update code: %s" % kind)
			else:
				pass
		self.WalkTree(self.root, CheckNode)

	def UpdateSome(self, changes = None):
		if changes:
			for kind, data in changes:
				self.UpdateOne(kind, data)
		else:
			self.UpdateAll()

	def NotifyObserver(self):
		if self.onNewSpecialCallback:
			self.onNewSpecialCallback(self.GetSpecials())

	def GetSpecials(self):
		specials = []
		(child, cookie) = self.tree.GetFirstChild(self.root)
		while child.IsOk():
			specials.append(self.tree.GetPyData(child))
			(child, cookie) = self.tree.GetNextChild(self.root, cookie)
		return specials

	def IsModifiable(self, item):
		unmodifiable = (Record.Record, Record.Page, Record.Hit)
		data = self.tree.GetPyData(item)
		return data.__class__ not in unmodifiable

	def UnderModifiable(self, item):
		parentItem = self.tree.GetItemParent(item)
		return self.IsModifiable(parentItem)

	def IsCloneable(self, item):
		uncloneable = (Record.Record, Record.Page, Record.Hit)
		data = self.tree.GetPyData(item)
		return data.__class__ not in uncloneable

if __name__ == '__main__':
	import Test
	import Project
	def init(p):
		p.project = Project.NoneProject()
	Test.TestPanel(SpecialsPanel, init)

# vim: foldmethod=marker:
