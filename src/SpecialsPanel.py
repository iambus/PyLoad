
import wx
from Special import Special
import Controller
import Player
import Record
from Tree import Tree
from FlyFrame import fly
from Changes import make_change, remove_change
import Search

import IconImages

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
			for uuid in data.split():
				self.panel.DropNewData(item, uuid)
			#XXX: why I have to set it none?
			self.controllerData.SetData('')
		if self.specialData.GetData():
			nodeIDs = map(int, self.specialData.GetData().split())
			self.panel.MoveNodes(item, nodeIDs)
			#XXX: why I have to set it none?
			self.specialData.SetData('')

		return d  
# }}}

class SpecialsPanel(wx.Panel):
	# {{{ init
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1)
		
		self.InitTree()

		# drag and drop
		self.SetDropTarget(MyDropTarget(self))
		self.tree.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnBeginDrag)
	

		# bindings
		self.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.OnBeginEdit, self.tree)
		self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnEndEdit, self.tree)

		self.tree.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
		self.tree.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
		#self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

		self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self.tree)
		self.onSelChangedCallback = None

		self.onNewSpecialCallback = None


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
		box.Add(self.search, 0, wx.EXPAND|wx.ALL, 5)
		self.SetSizer(box)



	def InitTree(self):
		self.tree = Tree(self, multiple = True)
		self.root = self.tree.root

		# FIXME: duplicated code in RecordPanel.py
		import ContentTypeHandler
		icons = {
				Special       : (IconImages.getSpecialOffBitmap(),
								 IconImages.getSpecialBitmap()),

				Record.Record : IconImages.getRecordBitmap(),
				Record.Page   : IconImages.getPageBitmap(),
				Record.Hit    : IconImages.getHitBitmap(),

				Controller.Script: IconImages.getScriptBitmap(),
				Controller.If    : IconImages.getIfBitmap(),
				Controller.Loop  : IconImages.getLoopBitmap(),
				Controller.Block : IconImages.getBlockBitmap(),

				ContentTypeHandler.DefaultContentType : IconImages.getWebBitmap(),
				ContentTypeHandler.AMFContentType     : IconImages.getFlexBitmap(),
				ContentTypeHandler.HTMLContentType    : IconImages.getWebBitmap(),
				ContentTypeHandler.XMLContentType     : IconImages.getWebBitmap(),
				ContentTypeHandler.PythonContentType  : IconImages.getWebBitmap(),
				ContentTypeHandler.BinContentType     : IconImages.getWebBitmap(),
				}
		self.tree.SetIcons(icons)

		def GetType(data):
			if isinstance(data, Record.Hit):
				# TODO: this check is for compatibility, remove it in future
				if isinstance(data.req_handler, ContentTypeHandler.ContentType):
					return data.req_handler.__class__
				else:
					# You see, really dirty trick,  so remove it in future...
					if 'AMF' in str(data.req_handler.coder):
						return ContentTypeHandler.AMFContentType
					else:
						return data.__class__
			else:
				return data.__class__

		self.tree.GetType = GetType


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
		nodes = self.tree.GetSelectedRoots()

		datas = map(self.tree.GetPyData, nodes)
		classes = [data.__class__ for data in datas]
		if any(map(lambda c: c == Special, classes)) and any(map(lambda c: c != Special, classes)):
			return event.Veto()

		if not any(map(self.IsMoveable, nodes)):
			return event.Veto()

		nodeIDs = map(str, map(id, nodes))
		self.dragging_items = nodes # FIXME: bad trick

		def DoDragDrop():
			dd = wx.CustomDataObject("special")
			dd.SetData(' '.join(nodeIDs))

			data = wx.DataObjectComposite()
			data.Add(dd)

			dropSource = wx.DropSource(self)
			dropSource.SetData(data)
			result = dropSource.DoDragDrop(wx.Drag_AllowMove)

		#wx.CallAfter(DoDragDrop) # XXX: not working on Linux
		DoDragDrop()

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
		item, flags = self.tree.HitTest(event.GetPosition())
		if item and not self.tree.IsSelected(item):
			self.tree.UnselectAll()
			self.tree.SelectItem(item)

	def OnRightUp(self, event):
		if not hasattr(self, "popupID1"):
			self.popupID1 = wx.NewId()
			self.popupID2 = wx.NewId()
			self.popupID3 = wx.NewId()
			self.popupID4 = wx.NewId()
			self.Bind(wx.EVT_MENU, self.OnNewSpecial, id=self.popupID1)
			self.Bind(wx.EVT_MENU, self.OnDeleteItems, id=self.popupID2)
			self.Bind(wx.EVT_MENU, self.OnDuplicateItem, id=self.popupID3)
			self.Bind(wx.EVT_MENU, self.OnFly, id=self.popupID4)

		menu = wx.Menu()
		menu.Append(self.popupID1, "New Special")

		#item, flags = self.tree.HitTest(event.GetPosition())
		nodes = self.tree.GetAllSelected()
		if len(nodes) > 0:
			if len(nodes) > 1:
				if any(map(self.UnderModifiable, nodes)):
					menu.Append(self.popupID2, "Delete")
			else:
				item = nodes[0]
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

	def OnDeleteItems(self, event):
		items = self.tree.GetSelectedRoots()
		items = filter(self.UnderModifiable, items)
		map(self.DeleteItem, items)

	def OnDuplicateItem(self, event):
		item = self.tree.GetSelected()
		if item:
			self.DuplicateItem(item)
			
	def OnFly(self, event):
		item = self.tree.GetSelected()
		assert item
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

	# {{{ Add new nodes
	@make_change
	def AppendNewSpecial(self):
		special = Special()
		self.project.add_special(special)
		special.label = 'New Special'
		self.tree.UnselectAll()
		item = self.tree.AddNode(self.root, special)
		self.tree.SelectItem(item)
		# XXX: why do I have to load it manually?
		if self.onSelChangedCallback:
			self.onSelChangedCallback(special)


	def InsertNewController(self, item, controller):
		itemData = self.tree.GetPyData(item)
		itemData.add_child(controller)

		label = controller.__class__.__name__
		controller.label = label

		self.LoadData(item, controller)

		self.tree.Expand(item)


	def UseData(self, item, data):
		parentData = self.tree.GetPyData(item)
		parentData.add_child(data)

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
				children = parentData.children
				index = self.tree.IndexOf(targetItem, parentItem)
				children.insert(index+1, sourceData)
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
	def MoveNodes(self, targetItem, sourceItems):
		sourceItems = self.dragging_items
		self.dragging_items = None

		targetData = self.tree.GetPyData(targetItem)
		targetParentItem = self.tree.GetItemParent(targetItem)
		if not self.IsModifiable(targetParentItem):
			#print "Can't modify partent"
			return

		sourceItems = filter(self.IsMoveable, sourceItems)
		sourceItems = filter(lambda s: s != targetItem, sourceItems)
		if any(map(lambda s: self.tree.CanReach(targetItem, s), sourceItems)):
			# can't put a father under child
			#print "can't put a father under child"
			return
		if not sourceItems:
			#print "Nothing to move"
			return

		sourceItem = sourceItems[0]
		sourceItems = sourceItems[1:]
		sourceData = self.tree.GetPyData(sourceItem)

		sourceParentItem = self.tree.GetItemParent(sourceItem)

		if sourceData.__class__ == Special:
			if targetData.__class__ == Special:
				sourceItems.reverse()
				for nextItem in sourceItems:
					self.MoveAfter(nextItem, targetItem)
				self.MoveAfter(sourceItem, targetItem)
			else:
				# You can only move a special after another special
				#print "You can only move a special after another special"
				pass
		elif self.IsModifiable(targetItem):
			self.MoveUnder(sourceItem, targetItem)
			for nextItem in sourceItems:
				self.MoveUnder(nextItem, targetItem)
		else:
			sourceItems.reverse()
			for nextItem in sourceItems:
				self.MoveAfter(nextItem, targetItem)
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
			children = parentData.children
		else:
			children = self.project.specials

		index = self.tree.IndexOf(targetItem, parentItem)
		children.insert(index+1, sourceData)

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

		if parentItem != self.root and self.tree.GetChildrenCount(parentItem, recursively = False) == 1:
			self.tree.Collapse(parentItem)
		index = self.tree.IndexOf(item, parentItem)
		self.tree.Delete(item)
		if parentData:
			parentData.remove_child(data, index)
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
			children = parentData.children
		else:
			children = self.project.specials

		index = self.tree.IndexOf(oldItem, parentItem)
		children.insert(index+1, newData)

		self.InsertData(parentItem, oldItem, newData)
	# }}}

	# {{{ Load kinds of Data (the data to be loaded should have been added as parent node's child)
	@make_change
	def LoadData(self, item, data):
		self.tree.AddTree(item, data)

	def LoadSpecial(self, item, s):
		self.tree.AddTree(item, s)


	# }}}

	# {{{ Insert kinds of Data AFTER a node (the data to be loaded should have been added as parent node's child)
	#FIXME: bad names -- why "insert" suppose "the data to be loaded should have been added as parent node's child"?
	@make_change
	def InsertData(self, item, prev, data):
		self.tree.InsertTree(item, prev, data)

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
		for child in special.children:
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
					if not data.children:
						self.tree.Collapse(node)
					self.tree.DeleteChildren(node)
					for child in data.children:
						self.LoadData(node, child)
					return True
				elif kind == 'a':
					self.tree.DeleteChildren(node)
					for child in data.children:
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
		unmodifiable = (Record.Record, Record.Page, Record.Hit, Controller.Script)
		data = self.tree.GetPyData(item)
		return data.__class__ not in unmodifiable

	def IsMoveable(self, item):
		return self.UnderModifiable(item)

	def UnderModifiable(self, item):
		parentItem = self.tree.GetItemParent(item)
		return self.IsModifiable(parentItem)

	def IsCloneable(self, item):
		return self.UnderModifiable(item)

if __name__ == '__main__':
	import Test
	import Project
	def init(p):
		p.project = Project.NoneProject()
	Test.TestPanel(SpecialsPanel, init)

# vim: foldmethod=marker:
