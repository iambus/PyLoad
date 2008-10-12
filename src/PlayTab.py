
import wx
from DetailsPanel import DetailsPanel
import PlayPolicy

class Choice(wx.Choice):
	def __init__(self, parent):
		wx.Choice.__init__(self, parent, -1, choices = [])

		self.values = []
		self.labels = []

		self.selected = None

		self.Bind(wx.EVT_CHOICE, self.OnSelected, self)
	
	def UpdateChoices(self, values, labels = None):
		if labels == None:
			labels = values
		assert len(values) == len(labels)
		self.values = values
		self.labels = labels

		self.Clear()
		for label in labels:
			self.Append(label)
		for i in range(len(values)):
			if values[i] is self.selected:
				self.SetSelection(i)
				return
		self.selected = None

	def GetData(self):
		return self.selected

	def OnSelected(self, event):
		self.selected = self.values[event.Selection]

class PolicyPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1)

		x1 = wx.StaticText(self, -1) #FIXME: dirty
		x2 = wx.StaticText(self, -1) #FIXME: dirty

		userLabel = wx.StaticText(self, -1, 'Users')
		userField = wx.SpinCtrl(self, -1)
		userField.SetRange(1,100)
		userField.SetValue(1)

		iterationLabel = wx.StaticText(self, -1, 'Iterations')
		iterationField = wx.SpinCtrl(self, -1)
		iterationField.SetRange(1,100)
		iterationField.SetValue(1)

		specialLabel = wx.StaticText(self, -1, 'Special')
		specialField = Choice(self)

		self.userField = userField
		self.iterationField = iterationField
		self.specialField = specialField

		sizer = wx.FlexGridSizer(cols=2, hgap=10, vgap=10)
		sizer.AddGrowableCol(1)
		sizer.AddMany([
			#XXX: wx.ALIGN_CENTRE|wx.ALIGN_RIGHT should be wrong
			(            x1, 0, wx.ALIGN_CENTRE|wx.ALIGN_RIGHT), (            x2, 0, wx.EXPAND), #FIXME: dirty
			(     userLabel, 0, wx.ALIGN_CENTRE|wx.ALIGN_RIGHT), (     userField, 0, wx.EXPAND),
			(iterationLabel, 0, wx.ALIGN_CENTRE|wx.ALIGN_RIGHT), (iterationField, 0, wx.EXPAND),
			(  specialLabel, 0, wx.ALIGN_CENTRE|wx.ALIGN_RIGHT), (  specialField, 0, wx.EXPAND),
			])

		box = wx.BoxSizer()

		self.SetSizer(sizer)
		self.SetAutoLayout(True)

	def UpdateSpecials(self, specials):
		specials = specials
		labels = []
		for s in specials:
			labels.append(s.label)
		self.specialField.UpdateChoices(specials, labels)


class EachPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1)

		self.list = wx.ListCtrl(self, -1,
				style=wx.LC_LIST 
				#| wx.BORDER_SUNKEN
				#| wx.BORDER_NONE
				#| wx.LC_EDIT_LABELS
				#| wx.LC_SORT_ASCENDING
				#| wx.LC_NO_HEADER
				#| wx.LC_VRULES
				#| wx.LC_HRULES
				| wx.LC_SINGLE_SEL
				)

		self.imagelist = wx.ImageList(16, 16)
		self.imagelist.Add(wx.ArtProvider_GetBitmap(wx.ART_NEW, wx.ART_OTHER, (16,16)))
		self.imagelist.Add(wx.ArtProvider_GetBitmap(wx.ART_QUESTION, wx.ART_OTHER, (16,16)))
		self.imagelist.Add(wx.ArtProvider_GetBitmap(wx.ART_REDO, wx.ART_OTHER, (16,16)))

		self.list.SetImageList(self.imagelist, wx.IMAGE_LIST_SMALL)

		self.list.InsertImageStringItem(0, 'Global', 0)
		self.list.InsertImageStringItem(1, 'Each User', 0)
		self.list.InsertImageStringItem(2, 'Each Iteration', 0)

		import Layout
		Layout.SingleLayout(self, self.list)


class PlayTab(wx.Panel):
	def __init__(self, parent, project = None, reporter = None):
		wx.Panel.__init__(self, parent, -1)

		self.splitter = wx.SplitterWindow(self, style=wx.BORDER_NONE)

		self.splitter2 = wx.SplitterWindow(self.splitter, style=wx.BORDER_NONE)
		p1 = PolicyPanel(self.splitter2)
		p2 = EachPanel(self.splitter2)
		self.splitter2.SetMinimumPaneSize(10)

		p3 = DetailsPanel(self.splitter)
		self.splitter.SetMinimumPaneSize(20)
		self.splitter.SplitVertically(self.splitter2, p3, 240)

		self.splitter2.SplitHorizontally(p1, p2, 120)

		self.policyPanel = p1
		self.eachPanel = p2
		self.detailsPanel = p3

		import Layout
		Layout.SingleLayout(self, self.splitter)

		# binding
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.eachPanel.list)
		self.Bind(wx.EVT_BUTTON, self.OnTestPlay, self.detailsPanel.testButton)

		#XXX: create new, or load from project?
		import PlayPolicy
		self.globalFactory = PlayPolicy.GlobalFactory()
		self.userFactory = PlayPolicy.UserFactory()
		self.iterationFactory = PlayPolicy.IterationFactory()

		if project:
			project.global_factory = self.globalFactory
			project.user_factory = self.userFactory
			project.iteration_factory = self.iterationFactory
		self.project = project
		self.reporter = reporter

	def OnItemSelected(self, event):
		self.selectedFactory = [self.globalFactory, self.userFactory, self.iterationFactory][event.Index]
		self.detailsPanel.Load(self.selectedFactory)

	def OnTestPlay(self, event):
		self.selectedFactory.test_play()

	def ResetSize(self):
		self.splitter.SetSashPosition(200)
		self.splitter2.SetSashPosition(120)

	def Unload(self):
		self.globalFactory = None
		self.userFactory = None
		self.iterationFactory = None
		self.detailsPanel.Unload()
		self.policyPanel.specialField.UpdateChoices([],[])

	def Reload(self):
		self.globalFactory = self.project.global_factory
		self.userFactory = self.project.user_factory
		self.iterationFactory = self.project.iteration_factory

	def Play(self):
		if self.policyPanel.specialField.GetData() == None:
			return

		userCount = self.policyPanel.userField.GetValue()
		iterationCount = self.policyPanel.iterationField.GetValue()
		special = self.policyPanel.specialField.GetData()
		userFactory = self.userFactory
		iterationFactory = self.iterationFactory
		globalFactory = self.globalFactory
		reporter = self.reporter
		policy = PlayPolicy.IterationBasedPlayPolicy(
				player = special,
				user_count = userCount,
				iteration_count = iterationCount,
				user_factory = userFactory,
				iteration_factory = iterationFactory,
				global_factory = globalFactory,
				reporter = reporter
				)
		policy.play()


if __name__ == '__main__':
	import Record
	import Project
	def init(p):
		pass
	import Test
	Test.TestPanel(PlayTab, init)

