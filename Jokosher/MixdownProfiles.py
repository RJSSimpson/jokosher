#
#	THIS FILE IS PART OF THE JOKOSHER PROJECT AND LICENSED UNDER THE GPL. SEE
#	THE 'COPYING' FILE FOR DETAILS
#
#	Jokosher Mixdown Profiles objects.
#
#-------------------------------------------------------------------------------

import Globals
import os
import pygtk
pygtk.require("2.0")
import gtk

import gettext
_ = gettext.gettext

class MixdownProfile:
	name = None # is a string when saved
	filename = None # is a filename when saved, file found in ~/.jokosher/mixdownprofiles/
	actions = [] # list of MixdownAction objects that make up this profile

	def load(self,filename):
		self.filename = filename
		# load the profile details from filename, creating all the actions and putting 
		# them in self.actions

	def save(self):
		if not self.filename: return
		# save this profile to self.filename
		# this is called whenever anything changes (instant apply)

	def run(self):
		datadict = {}
		for action in self.actions:
			self.action.run(datadict)

class MixdownAction:
	"""this class is available to extensions, which will be able to create new 
	actions to be added to profiles by subclassing it"""
	def __init__(self):
		self.config = {} # a dictionary of configuration options that this action needs
								# public because MixdownProfile.save() needs to save it
								# and so we can autogenerate a config GUI for it if we have to 
								# (although this is not recommended)
		self.button = None # our config button. This gets set by the Dialog.
	
	def configure(self):
		""" pops up a configuration window. Creates an autogenerated GUI. Subclasses 
		should override this to do sensible configuration rather than nasty 
		autogenerated configuration."""
		
		w = gtk.Window()
		vb = gtk.VBox()
		w.add(vb)
		for k,v in self.config.items():
			h = gtk.HBox()
			h.add(gtk.Label(k))
			e = gtk.Entry()
			e.set_text(v)
			e.connect("focus-out-event", self.__configEntryChanged, k)
			h.add(e)
			vb.add(h)
		w.connect("delete_event", self.__finishConfiguration)
		w.show_all()
		
	def __finishConfiguration(self, widget, event):
		"Internal function to update our button on the Mixdown window"
		widget.destroy()
		self.update_button()

	def __configEntryChanged(self, widget, event, datakey):
		"Internal function to update our config dictionary"
		self.config[datakey] = widget.get_text()

	def update_button(self):
		"Update our button on the mixdown window"
		self.button.set_label(self.display_name())

	@staticmethod
	def create_name():
		"""A name for this action, to go in the choose-an-action menu"""
		return "Export file"

	def run(self, data):
		"""do whatever this action actually does. data is a dictionary populated 
		by earlier Actions in this Profile, as described below. It can manipulate 
		the data dictionary how it likes."""
		pass

	def display_name(self):
		"""return my name, for display in the button in the Profile window
		this is a function because an "Upload to..." Action should call itself
		"Upload to mysshserver" if it's been configured already, for example"""
		return "An unspecified MixdownAction"

	def is_configured(self):
		"""returns True if this Action thinks it has been configured correctly,
		False if not"""
		return False
		
	def serialise(self):
		"""Return an XML description of this action, with its parameters"""
		paramxml = "<%s>%s</%s>"
		outerxml = "<%s>%s</%s>"
		params = [paramxml % (x,self.config[x],x) for x in self.config.keys()]
		return outerxml % (self.__class__.__name__, '\n'.join(params), 
											 self.__class__.__name__)

class ExportAsFileType(MixdownAction):
	def __init__(self, project):
		"""Special init function for this particular MixdownAction, which takes
		a reference to the project as a parameter; this is so we can call back
		into the project to do the export. This means that the core code must
		special-case action creation, and if it's creating one of these then
		pass it a project.
		
		Parameters:
			project -- the current Jokosher project
		"""
		MixdownAction.__init__(self)
		# Always start with ogg as the filetype
		self.filetypedict = [x for x in Globals.EXPORT_FORMATS if x['extension'] == 'ogg'][0]
		self.config["filename"] = os.path.expanduser("~/export.ogg")
		self.config["filetype"] = self.filetypedict['extension']
		self.project = project # note: this is special to this action, and needs
		                       # to be passed, so this action needs special handling
		                       # in the core.
	
	def display_name(self):
		"See MixdownAction.display_name"
		return _("Export to %s as %s") % (
			os.path.split(self.config["filename"])[1],
			self.filetypedict["description"])

	@staticmethod
	def create_name():
		"See MixdownAction.create_name"
		return _("Export file")

	def run(self,data):
		"See MixdownAction.run"
		data["filename"] = self.config["filename"]
		data["filetype"] = self.filetypedict["extension"]
		self.project.Export(self.config["filename"], self.filetypedict["pipeline"])
		
	def configure(self):
		"See MixdownAction.configure"
		buttons = (gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK)
		chooser = gtk.FileChooserDialog(_("Export as"), None, gtk.FILE_CHOOSER_ACTION_SAVE, buttons)
		chooser.set_current_folder(os.path.expanduser("~"))
		chooser.set_do_overwrite_confirmation(True)
		chooser.set_default_response(gtk.RESPONSE_OK)
		chooser.set_current_name(os.path.split(self.config["filename"])[1])

		saveLabel = gtk.Label(_("Save as file type:"))		
		typeCombo = gtk.combo_box_new_text()
		
		counter = 0
		active_item = 0
		for format in Globals.EXPORT_FORMATS:
			typeCombo.append_text("%s (.%s)" % (format["description"], format["extension"]))
			if format == self.filetypedict:
				active_item = counter
			counter += 1
		typeCombo.set_active(active_item)
		
		extraHBox = gtk.HBox()
		extraHBox.pack_start(saveLabel, False)
		extraHBox.pack_end(typeCombo, False)
		extraHBox.show_all()
		chooser.set_extra_widget(extraHBox)
		
		response = chooser.run()
		if response == gtk.RESPONSE_OK:
			self.config["filename"] = chooser.get_filename()
			Globals.settings.general["projectfolder"] = os.path.dirname(self.config["filename"])
			Globals.settings.write()
			#If they haven't already appended the extension for the 
			#chosen file type, add it to the end of the file.
			filetypeDict = Globals.EXPORT_FORMATS[typeCombo.get_active()]
			if not self.config["filename"].lower().endswith(filetypeDict["extension"]):
				self.config["filename"] += "." + filetypeDict["extension"]
			chooser.destroy()
			self.update_button()
		else:
			chooser.destroy()	

class RunAScript(MixdownAction):
	def __init__(self):
		"See MixdownAction.__init__"
		MixdownAction.__init__(self)
		self.config["script"] = os.path.expanduser("~/jokscript.sh")
	
	def display_name(self):
		"See MixdownAction.display_name"
		return _("Run script %s") % (os.path.split(self.config["script"])[1])
	
	@staticmethod
	def create_name():
		"See MixdownAction.create_name"
		return _("Run external script")

	def run(self,data):
		"See MixdownAction.run"
		# Set up the environment for the process by putting all of the
		# vars from the mixdownprofile in it as JOKOSHER_* vars
		subprocess_environment = {}
		for k,v in data.items():
			subprocess_environment["JOKOSHER_%s" % k.upper()] = v
		import subprocess
		try:
			# needs to happen in a thread!
			subprocess.Popen(self.config["script"], env=subprocess_environment, shell=True).wait()
			# have to get the subprocess's environment after it's finished. How?
		except OSError:
			raise _("No such script %s") % self.config["script"], e
		except:
			raise _("Error in script %s") % self.config["script"]
		for k,v in subprocess_environment.items(): # this won't work until we have the s.p.'s env
			if k.startswith("JOKOSHER_"):
				varname = k[9:].lower() # strip off JOKOSHER_
				data[varname] = v
		
