
import wx

def XTimeFormatter(s, max = None):
	if max and max < 60:
		return '%ds' % s
	elif max and max < 3600:
		return '%02dm:%02ds' % ((s/60)%60, s%60)
	return '%02d:%02d:%02d' % (s/3600, (s/60)%60, s%60)

def YMSFormatter(ms, max = None):
	if (max and max >= 1000) or ms >= 1000:
		s = ms / 1000.0
		return '%ss' % s
	else:
		return '%sms' % ms

def DefaultFormatter(x, max = None):
	return str(x)


wShift = 40 # left
hShift = 30 # bottom
tShift = 10 # top
rShift = 10 # right

def getDataAreaSize(dc):
	w, h = dc.GetSize()
	w, h = w - wShift - rShift, h - hShift - tShift
	return w, h

def getXYAreaSize(dc):
	w, h = dc.GetSize()
	w, h = w - wShift, h - hShift
	return w, h


class LineChart(wx.Panel): 
	def __init__(self, parent, times = None):
		wx.Panel.__init__(self, parent)
		self.SetBackgroundColour('WHITE')

		self.times = times
		if self.times:
			self.times = sorted(self.times)

		self.xformat = DefaultFormatter
		self.yformat = DefaultFormatter

		self.showAll = True

		self.InitData()
		self.InitBuffer()

		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_IDLE, self.OnIdle)

		self.Bind(wx.EVT_RIGHT_DCLICK, self.OnSwitchLines)

	def InitData(self):
		if self.times == None:
			return

		from itertools import groupby
		from operator import itemgetter

		self.data = sorted([(i[0]/1000, i[1]) for i in self.times])
		if self.times and self.times[-1][0] > 600 * 1000:
			self.data = [(i[0] - i[0]%10 + 5, i[1]) for i in self.data]
		else:
			self.data = [(i[0] + 1, i[1]) for i in self.data]

		self.groups = [(k, zip(*g)[1]) for k, g in groupby(self.data, key=itemgetter(0))]
		self.max = [(k, max(v)) for k, v in self.groups]
		self.min = [(k, min(v)) for k, v in self.groups]
		self.avg = [(k, sum(v)/len(v)) for k, v in self.groups]

		self.xmax = max(zip(*self.data)[0])
		self.ymax = max(zip(*self.data)[1])

		if self.xmax < 30:
			self.xi = 1
		elif self.xmax < 60 * 10:
			self.xi = 30
		else:
			self.xi = 60 * 2

		self.xmax = (self.xmax / self.xi + 1) * self.xi

		if self.ymax < 1000:
			self.yi = 100
		elif self.ymax < 1000 * 2:
			self.yi = 200
		elif self.ymax < 1000 * 5:
			self.yi = 500
		elif self.ymax < 1000 * 10:
			self.yi = 1000
		elif self.ymax < 1000 * 60:
			self.yi = 5000
		elif self.ymax < 1000 * 120:
			self.yi = 1000 * 10
		else:
			self.yi = 1000 * 30

		self.ymax = (self.ymax / self.yi + 1) * self.yi

	def InitBuffer(self):
		size = self.GetClientSize()
		self.buffer = wx.EmptyBitmap(size.width, size.height)
		dc = wx.BufferedDC(None, self.buffer)
		dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
		dc.Clear()

		self.DrawAll(dc)
		self.reInitBuffer = False

	# Event handlers
	def OnSize(self, event):
		self.reInitBuffer = True

	def OnIdle(self, event):
		if self.reInitBuffer:
			self.InitBuffer()
			self.Refresh(False)

	def OnPaint(self, event):
		dc = wx.BufferedPaintDC(self, self.buffer)

	def OnSwitchLines(self, event):
		self.showAll = not self.showAll
		self.reInitBuffer = True

	# Drawing
	def DrawAll(self, dc):
		if self.times == None:
			return

		w, h = dc.GetSize()
		dc.SetDeviceOrigin(wShift, h-hShift)
		dc.SetAxisOrientation(True, True)
		dc.SetPen(wx.Pen('WHITE'))
		#dc.DrawRectangle(1, 1, w, h) #XXX? what

		self.DrawGrid(dc)
		self.DrawAxis(dc)
		#self.DrawTitle(dc)
		self.DrawData(dc)

	def DrawAxis(self, dc):
		w, h = getDataAreaSize(dc)
		ww, hh = getXYAreaSize(dc)
		if w <= 0 or h <= 0:
			return

		dc.SetPen(wx.Pen('#0AB1FF'))
		font = dc.GetFont()
		font.SetPointSize(8)
		dc.SetFont(font)
		dc.DrawLine(0, 0, ww, 0)
		dc.DrawLine(0, 0, 0, hh)

		for i in range(self.xi, self.xmax+1, self.xi):
			x = w * i / self.xmax
			dc.DrawLine(x, 1, x, -5)
			dc.DrawText(self.xformat(i, self.xmax), x-13, -10)

		for i in range(self.yi, self.ymax+1, self.yi):
			y = h * i / self.ymax
			dc.DrawLine(1, y, -5, y)
			dc.DrawText(self.yformat(i, self.ymax), -30, y)

	def DrawGrid(self, dc):
		w, h = getDataAreaSize(dc)
		ww, hh = getXYAreaSize(dc)
		dc.SetPen(wx.Pen('#d5d5d5'))

		for i in range(self.xi, self.xmax+1, self.xi):
			x = w * i / self.xmax
			dc.DrawLine(x, 0, x, hh)

		for i in range(self.yi, self.ymax+1, self.yi):
			y = h * i / self.ymax
			dc.DrawLine(0, y, ww, y)

	def DrawTitle(self, dc):
		w, h = getDataAreaSize(dc)
		font =  dc.GetFont()
		font.SetWeight(wx.FONTWEIGHT_BOLD)
		dc.SetFont(font)
		dc.DrawText('Some Text...', 90, 235)


	def DrawData(self, dc):
		if self.showAll:
			dc.SetPen(wx.Pen('#ff7272', 2))
			self.DrawLine(dc, self.max)

			dc.SetPen(wx.Pen('#E0CD78', 2))
			self.DrawLine(dc, self.min)

		dc.SetPen(wx.Pen('#8ccbea', 2))
		self.DrawLine(dc, self.avg)


	def DrawLine(self, dc, lineData):
		w, h = getDataAreaSize(dc)

		points = [(0,0)]
		points.extend(lineData)
		points.append(points[-1])

		xv = float(w) / self.xmax
		yv = float(h) / self.ymax

		#dc.DrawSpline([(x*xv, y*yv) for x, y in points])
		dc.DrawLines([(x*xv, y*yv) for x, y in points])

	def SetData(self, times):
		self.times = times
		if self.times:
			self.times = sorted(self.times)
		self.InitData()
		self.reInitBuffer = True


if __name__ == '__main__':
	times = ((116, 173), 
			(121, 216), 
			(1401, 208), 
			(1431, 400), 
			(1508, 225), 
			(1409, 214), 
			(1700, 228), 
			(1850, 238), 
			(1890, 274),
			(1960, 272), 
			(2600, 376), 
			(3000, 200), 
			)

	import Test
	Test.TestPanel(LineChart, lambda p: p.SetData(times))

