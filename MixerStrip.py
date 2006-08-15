
import pygtk
pygtk.require("2.0")
import gtk
import os
import Globals

import gettext
_ = gettext.gettext

from VUWidget import *

#=========================================================================

class MixerStrip(gtk.Frame):
	
	__gtype_name__ = 'MixerStrip'
	
	#_____________________________________________________________________
	
	def __init__(self, project, instrument, mixview, mainview):
		gtk.Container.__init__(self)
		self.project = project
		self.instrument = instrument
		self.mixview = mixview
		self.mainview = mainview
		self.Updating = False
		
		self.vbox = gtk.VBox()
		self.add(self.vbox)

		self.minbutt = gtk.Button()
		img = gtk.image_new_from_stock(gtk.STOCK_GOTO_BOTTOM, gtk.ICON_SIZE_MENU)
		self.minbutt.set_image(img)
		self.mintip = gtk.Tooltips()
		self.mintip.set_tip(self.minbutt, _("Minimize instrument"), None)
		self.minbutt.connect("clicked", self.EmitMinimise)
				
		self.vbox.pack_start(self.minbutt, False)
		
		# VU Meter
		self.vu = VUWidget(self, self.mainview)
		self.vbox.pack_start(self.vu, True, True)
		
		#Control Buttons
		hb = gtk.HBox()
			
		img = gtk.image_new_from_stock(gtk.STOCK_MEDIA_RECORD, gtk.ICON_SIZE_BUTTON)
		self.recButton = gtk.ToggleButton("")
		self.recButton.set_property("image", img)
		self.recButton.connect("toggled", self.OnArm)
		self.recTip = gtk.Tooltips()
		self.recTip.set_tip(self.recButton, _("Enable this instrument for recording"), None)

		self.muteButton = gtk.ToggleButton("")
		self.muteButton.connect("toggled", self.OnMute)
		self.muteTip = gtk.Tooltips()
		self.muteTip.set_tip(self.muteButton, "Mute - silence this instrument", None)
		
		soloimg = gtk.Image()
		soloimg.set_from_file(os.path.join(Globals.IMAGE_PATH, "solo.png"))
		self.soloButton = gtk.ToggleButton("")
		self.soloButton.set_image(soloimg)
		self.soloTip = gtk.Tooltips()
		self.soloTip.set_tip(self.soloButton, _("Solo - silence all other instruments"), None)
		self.soloButton.connect("toggled", self.OnSolo)
		
		hb.add(self.recButton)
		hb.add(self.muteButton)
		hb.add(self.soloButton)
		self.vbox.pack_start(hb, False, False)
		
		# Label and icon
		hb = gtk.HBox()
		imgsize = gtk.icon_size_lookup(gtk.ICON_SIZE_MENU)[0]
		pixbuf = self.instrument.pixbuf.scale_simple(imgsize, imgsize, gtk.gdk.INTERP_BILINEAR)
		image = gtk.Image()
		image.set_from_pixbuf(pixbuf)
		hb.pack_start(image, False, False)
		
		self.label = gtk.Label(instrument.name)
		self.label.set_max_width_chars(6)
		hb.pack_start(self.label, True, True)
		
		self.vbox.pack_end(hb, False, False)
		self.vbox.show_all()
		self.show_all()
		
		self.Update()
		
	#_____________________________________________________________________

	def OnMute(self, widget):
		if not self.Updating:
			self.instrument.ToggleMuted(False)
	
	#_____________________________________________________________________

	def OnArm(self, widget):
		if not self.Updating:
			self.instrument.ToggleArmed()
		
	#_____________________________________________________________________
	
	def OnSolo(self, widget):
		if not self.Updating:
			self.instrument.ToggleSolo(False)
		
	#_____________________________________________________________________
	
	def EmitMinimise(self, widget):
		self.emit("minimise")
	
	#_____________________________________________________________________
	
	def Update(self):
		self.Updating = True
		
		self.mintip.enable()
		self.label.set_text(self.instrument.name)
		self.recButton.set_active(self.instrument.isArmed)
		self.recTip.enable()
		
		self.muteButton.set_active(self.instrument.actuallyIsMuted)
		if self.instrument.actuallyIsMuted:
			self.muteButton.set_image(gtk.image_new_from_icon_name("stock_volume-mute", gtk.ICON_SIZE_BUTTON))
			self.muteTip.set_tip(self.muteButton, _("Muted"), None)
		else:
			self.muteButton.set_image(gtk.image_new_from_icon_name("stock_volume", gtk.ICON_SIZE_BUTTON))
			self.muteTip.set_tip(self.muteButton, _("Unmuted"), None)
		
		
		self.soloButton.set_active(self.instrument.isSolo)
		self.soloTip.enable()
		
		self.Updating = False
	
	#_____________________________________________________________________

	def GetLevel(self):
		return self.instrument.level
		
	#_____________________________________________________________________

	def GetVolume(self):
		return self.instrument.volume
		
	#_____________________________________________________________________

	def SetVolume(self, vol):
		self.instrument.SetVolume(vol)
		
	#_____________________________________________________________________
	
#=========================================================================

