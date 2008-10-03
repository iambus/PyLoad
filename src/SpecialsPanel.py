
import wx
from Special import Special
import Controller
import Player
import Record

import Logger
log = Logger.getLogger()

# {{{ DropTarget
class MyDropTarget(wx.PyDropTarget):
	def __init__(self, panel):
		wx.PyDropTarget.__init__(self)
		self.panel = panel
		self.tree = self.panel.tree

		self.data = wx.CustomDataObject("xxx")
		self.SetDataObject(self.data)


	def OnEnter(self, x, y, d):
		return d

	def OnLeave(self):
		pass

	def OnDrop(self, x, y):
		return True

	def OnDragOver(self, x, y, d):
		return d


	def OnData(self, x, y, d):
		if not self.GetData():
			return d

		item, flags = self.tree.HitTest((x,y))
		if flags & wx.TREE_HITTEST_NOWHERE:
			log.debug('no place to drop')
			return d

		self.panel.DropData(item, self.data.GetData())
#		bits = {
#				wx.TREE_HITTEST_ABOVE : 'wx.TREE_HITTEST_ABOVE',
#				wx.TREE_HITTEST_BELOW : 'wx.TREE_HITTEST_BELOW',
#				wx.TREE_HITTEST_NOWHERE : 'wx.TREE_HITTEST_NOWHERE',
#				wx.TREE_HITTEST_ONITEMBUTTON : 'wx.TREE_HITTEST_ONITEMBUTTON',
#				wx.TREE_HITTEST_ONITEMICON : 'wx.TREE_HITTEST_ONITEMICON',
#				wx.TREE_HITTEST_ONITEMINDENT : 'wx.TREE_HITTEST_ONITEMINDENT',
#				wx.TREE_HITTEST_ONITEMLABEL : 'wx.TREE_HITTEST_ONITEMLABEL',
#				wx.TREE_HITTEST_ONITEMRIGHT : 'wx.TREE_HITTEST_ONITEMRIGHT',
#				wx.TREE_HITTEST_ONITEMSTATEICON : 'wx.TREE_HITTEST_ONITEMSTATEICON',
#				wx.TREE_HITTEST_TOLEFT : 'wx.TREE_HITTEST_TOLEFT',
#				wx.TREE_HITTEST_TORIGHT : 'wx.TREE_HITTEST_TORIGHT',
#		}
#		print bits[flags]

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
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1)
		
		self.InitTree()

		self.SetDropTarget(MyDropTarget(self))
	
		# layout
		import Layout
		Layout.SingleLayout(self, self.tree)

		# bindings
		self.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.OnBeginEdit, self.tree)
		self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnEndEdit, self.tree)

		self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

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

		self.tree.SetImageList(iconList)
		self.iconList = iconList
		self.root = self.tree.AddRoot("All Specials")
		self.tree.SetPyData(self.root, None)
		self.tree.SetItemImage(self.root, self.specialIcon, wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(self.root, self.specialOpenIcon, wx.TreeItemIcon_Expanded)

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

	def OnEndEdit(self, event):
		if event.EditCancelled:
			return
		item = event.GetItem()
		data = self.tree.GetPyData(item)
		assert type(data.label) == str or type (data.label) == unicode, 'Invalid label type:%s' % type(data.label)
		data.label = event.GetLabel()
		self.NotifyObserver()

	def OnSelChanged(self, event):
		self.item = event.GetItem()
		data = self.tree.GetPyData(self.item)
		if self.onSelChangedCallback:
			self.onSelChangedCallback(data)

	def OnContextMenu(self, event):
		if not hasattr(self, "popupID1"):
			self.popupID1 = wx.NewId()

			self.Bind(wx.EVT_MENU, self.OnNewSpecial, id=self.popupID1)

		menu = wx.Menu()
		menu.Append(self.popupID1, "New Special")

		self.PopupMenu(menu)
		menu.Destroy()

	def OnNewSpecial(self, event):
		self.AppendNewSpecial()
		self.NotifyObserver()
	# }}}

	def AppendNewSpecial(self):
		special = Special()
		special.label = 'New Special'
		specialItem = self.tree.AppendItem(self.root, "New Special")
		self.tree.SetPyData(specialItem, special)
		self.tree.SetItemImage(specialItem, self.specialIcon, wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(specialItem, self.specialOpenIcon, wx.TreeItemIcon_Expanded)

		self.tree.SelectItem(specialItem)

	def DropData(self, item, data):
		itemData = self.tree.GetPyData(item)

		# find a place to insert
		if not (isinstance(itemData, Special) or isinstance(itemData, Controller.Controller)):
			item = self.tree.GetItemParent(item)
			itemData = self.tree.GetPyData(item)
			if not (isinstance(itemData, Special) or isinstance(itemData, Controller.Controller)):
				log.debug('no place to insert')
				return

		import Repository
		data = Repository.lookup(data)
		import inspect
		if inspect.isclass(data):
			data = data()
			self.InsertNewController(item, data)
		else:
			self.UseData(item, data)

	def InsertNewController(self, item, controller):
		itemData = self.tree.GetPyData(item)
		itemData.add_child(controller)

		label = str(controller.__class__)
		label = label[label.rfind('.')+1:]
		controller.label = label

		self.LoadData(item, controller)

		self.tree.Expand(item)


	def UseData(self, item, data):
		parentdata = self.tree.GetPyData(item)
		parentdata.add_child(data)

		self.LoadData(item, data)

		self.tree.Expand(item)

	# {{{ Load kinds of Data (the data to be loaded should have been added as parent node's child)
	def LoadData(self, item, data):
		mappings = {
				Record.Record : self.LoadRecord,
				Record.Page : self.LoadPage,
				Record.Hit : self.LoadHit,
				Player.Script : self.LoadScript,
				Controller.If : self.LoadIf,
				Controller.Loop : self.LoadLoop,
				}
		mappings[data.__class__](item, data)

	def LoadRecord(self, item, r):
		recordItem = self.tree.AppendItem(item, "%s" % r.label)
		self.tree.SetPyData(recordItem, r)
		self.tree.SetItemImage(recordItem, self.recordIcon, wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(recordItem, self.recordOpenIcon, wx.TreeItemIcon_Expanded)

		for p in r.pages:
			self.LoadPage(recordItem, p)

		self.tree.Expand(recordItem)

	def LoadPage(self, item, p):
		pageItem = self.tree.AppendItem(item, p.path)
		self.tree.SetPyData(pageItem, p)
		self.tree.SetItemImage(pageItem, self.recordIcon, wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(pageItem, self.recordOpenIcon, wx.TreeItemIcon_Expanded)

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
	# }}}

	def ReloadSpecial(self, item):
		special = self.tree.GetPyData(item)
		self.tree.DeleteChildren(item)
		for child in special.childern:
			self.LoadData(item, child)

	def ReloadAll(self):
		(child, cookie) = self.tree.GetFirstChild(self.root)
		while child.IsOk():
			self.ReloadSpecial(child)
			(child, cookie) = self.tree.GetNextChild(self.root, cookie)


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

if __name__ == '__main__':
	import Test
	Test.TestPanel(SpecialsPanel)

# vim: foldmethod=marker:
