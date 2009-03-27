
import wx

class Tree(wx.TreeCtrl):
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

