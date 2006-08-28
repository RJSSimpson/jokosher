
import gtk
import InstrumentViewer
import TimeLineBar
import gobject
import Globals
import Monitored

#=========================================================================

class RecordingView(gtk.Frame):

	__gtype_name__ = 'RecordingView'
	INSTRUMENT_HEADER_WIDTH = 150

	#_____________________________________________________________________

	def __init__(self, project, mainview, mixView=None, small=False):
		gtk.Frame.__init__(self)

		self.project = project
		self.mainview = mainview
		self.mixView = mixView
		self.small = small
		self.timelinebar = TimeLineBar.TimeLineBar(self.project, self, mainview)

		self.vbox = gtk.VBox()
		self.add(self.vbox)
		self.vbox.pack_start(self.timelinebar, False, False)
		self.instrumentWindow = gtk.ScrolledWindow()
		self.instrumentBox = gtk.VBox()
		self.instrumentWindow.add_with_viewport(self.instrumentBox)
		self.instrumentWindow.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
		self.vbox.pack_start(self.instrumentWindow, True, True)
		self.instrumentWindow.child.set_shadow_type(gtk.SHADOW_NONE)
		self.views = []	
		
		self.hb = gtk.HBox()
		self.vbox.pack_end(self.hb, False, False)
		self.al = gtk.Alignment(0, 0, 1, 1)
		self.scrollRange = gtk.Adjustment()
		sb = gtk.HScrollbar(self.scrollRange)
		self.al.add(sb)
		self.al.set_padding(0, 0, 0, 0)
		self.hb.pack_start(self.al)
		if not self.mixView:
			zoom_out = gtk.ToolButton(gtk.STOCK_ZOOM_OUT)
			zoom = gtk.ToolButton(gtk.STOCK_ZOOM_100)
			zoom_in = gtk.ToolButton(gtk.STOCK_ZOOM_IN)
			self.hb.pack_start( zoom_out, False, False)
			self.hb.pack_start( zoom, False, False)
			self.hb.pack_start( zoom_in, False, False)
			zoom_out.connect("clicked", self.OnZoomOut)
			zoom.connect("clicked", self.OnZoom100)
			zoom_in.connect("clicked", self.OnZoomIn)
		
		self.scrollRange.lower = 0
		self.scrollRange.upper = 100
		self.scrollRange.value = 0
		self.scrollRange.step_increment = 1
		
		sb.connect("value-changed", self.OnScroll)
		self.connect("expose-event", self.OnExpose)
		self.connect("button_release_event", self.OnExpose)
		self.connect("button_press_event", self.OnMouseDown)
		self.connect("size-allocate", self.OnAllocate)
		
		self.Update()
	#_____________________________________________________________________

	def OnExpose(self, widget, event):
		""" Sets scrollbar properties once space has been allocated """
		
		# calculate scrollable width - allow 4 pixels for borders
		self.scrollRange.page_size = (self.allocation.width - Globals.INSTRUMENT_HEADER_WIDTH - 4) / self.project.viewScale
		self.scrollRange.page_increment = self.scrollRange.page_size
		length = self.project.GetProjectLength()
		self.scrollRange.upper = length
		# Need to adjust project view start if we are zooming out
		# and the end of the project is now before the end of the page.
		# Project end will be at right edge unless the start is also on 
		# screen, in which case the start will be at the left.
		if self.project.viewStart + self.scrollRange.page_size > length:
			start = max(0, length - self.scrollRange.page_size)
			self.scrollRange.value = start
			if start != self.project.SetViewStart:
				self.project.SetViewStart(start)
			
		
	#_____________________________________________________________________

	def OnAllocate(self, widget, allocation):
		self.allocation = allocation
		
	#_____________________________________________________________________
	

	def Update(self):
		# Note: InstrumentViews MUST have the order that the instruments have in
		#       Project.instruments to keep the drag and drop of InstrumentViews
		#       consistent!
		children = self.instrumentBox.get_children()
		orderCounter = 0
		for instr in self.project.instruments:
			#Find the InstrumentView that matches instr:
			iv = None
			for ident, instrV in self.views:
				if instrV.instrument is instr:
					iv = instrV
					break
			#If there is no InstrumentView for instr, create one:
			if not iv:
				iv = InstrumentViewer.InstrumentViewer(self.project, instr, self, self.mainview, self.small)
				# if this is mix view then add parent (CompactMixView) as listener
				# otherwise add self
				if self.mixView:
					instr.AddListener(self.mixView)
				else:
					instr.AddListener(self)
				#Add it to the views
				self.views.append((instr.id, iv))
				iv.headerAlign.connect("size-allocate", self.UpdateSize)
			
			if iv not in children:
				#Add the InstrumentView to the VBox
				self.instrumentBox.pack_start(iv, False, False)
			else:
				#If the InstrumentView has already been added, just move it
				self.instrumentBox.reorder_child(iv, orderCounter)
				
			#Make sure the InstrumentView is visible:
			iv.show()
			
			orderCounter += 1
			
		#self.views is up to date now
		for ident, iv in self.views:
			#check if instrument has been deleted
			if not iv.instrument in self.project.instruments and iv in children:
				self.instrumentBox.remove(iv)
			else:
				iv.Update() #Update non-deleted instruments
		
		
		if len(self.views) > 0:
			self.UpdateSize(None, self.views[0][1].headerAlign.get_allocation())
		else:
			self.UpdateSize(None, None)
		self.show_all()
	
	#_____________________________________________________________________
		
	def UpdateSize(self, widget=None, size=None):
		#find the width of the instrument headers (they should all be the same size)
		if size:
			tempWidth = size.width
		else:
			tempWidth = self.INSTRUMENT_HEADER_WIDTH
		
		#set it to the globals class so compactmix can use the same width
		Globals.INSTRUMENT_HEADER_WIDTH = tempWidth
		
		self.timelinebar.Update(tempWidth)
		self.al.set_padding(0, 0, tempWidth, 0)
	
	#_____________________________________________________________________
	
	def OnScroll(self, widget):
		pos = widget.get_value()
		self.project.SetViewStart(pos)

	#_____________________________________________________________________
		
	def OnZoomOut(self, widget):
		tmp = self.project.viewScale * 2. / 3
		if tmp > 0.5:
			self.project.viewScale = tmp
		self.project.SetViewScale(self.project.viewScale)
		
	#_____________________________________________________________________
		
	def OnZoom100(self, widget):
		self.project.SetViewScale(25.0)
		
	#_____________________________________________________________________
		
	def OnZoomIn(self, widget):
		tmp = self.project.viewScale * 1.5
		# Warning: change this value with caution increases
		# beyond 4000 are likely to cause crashes!
		if tmp < 4000:
			self.project.viewScale = tmp
		self.project.SetViewScale(self.project.viewScale)
				
	#_____________________________________________________________________

	def OnMouseDown(self, widget, mouse):
		# If we're here then we're out of bounds of anything else
		# So we should clear any selected events
		self.project.ClearEventSelections()
		self.project.ClearInstrumentSelections()
		self.Update()
		
	#_____________________________________________________________________
	
	def OnStateChanged(self, obj, change=None):
		self.Update()
		
	#_____________________________________________________________________	
#=========================================================================