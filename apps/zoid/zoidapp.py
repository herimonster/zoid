import zapp
import zframe
import ztextframe
import zlistbox
import ztextbox
import zquerybox
import zutils
import zsearchframe
import zregexhighlighter
import zhighlighterlist
import zfilebrowser

import zmessagebox

import os
import re
import pwd
import sys
import signal

import curses

import subprocess

class document:
	def __init__(self, parent):
		self._r = parent
		self.textedit = ztextframe.ztextframe(self._r, (0,0), self._r._size)
		self.textedit.set_catch_focus(False)
		
		self._name = "unknown"
		self._filename = ""
		
		self._r.add_child(self.textedit)
		
		self.textedit.on_change = self._on_changed
		#self.textedit._textedit.highlighter.load_rules("python")
		
		self.on_caption_change = None
		self.update_caption()
		#self.set_visible(False)
	
	
	
	def set_caption(self, caption):
		self._caption = caption
		if self.on_caption_change != None:
			self.on_caption_change(self)
	
	def get_caption(self):
		return self._caption
	
	def get_changed(self):
		return self.textedit._textedit.get_changed()
	
	def update_caption(self):
		if self.get_changed():
			self.set_caption("◉"+self._name)
		else:
			self.set_caption("○"+self._name)
	
	def _on_changed(self, sender):
		self.update_caption()
	
	def set_visible(self, is_visible):
		self.textedit.set_visible(is_visible)
	
	def load_from_file(self, fn):
		
		with open(fn, 'r', encoding='utf-8') as f:
			content = f.read()
		self.textedit._textedit.set_text(content)
		self._filename = fn
		self._name = os.path.basename(self._filename)
		self.update_caption()
		return True
		
	
	def save_to_file(self, fn):
		
		with open(fn, 'w', encoding='utf-8') as f:
			f.write(self.textedit._textedit.get_text())

		self._filename = fn
		self._name = os.path.basename(self._filename)
		self.textedit._textedit._set_unchanged()
		self.update_caption()
		return True
		
	def get_lines(self):
		return self.textedit._textedit._lines
	
	def get_cursor(self):
		return self.textedit._textedit.get_cursor()
	
	def get_sel(self):
		return self.textedit._textedit.get_cursor()
	
	def set_cursor(self, x, y, keep_sel = False):
		self.textedit._textedit.set_cursor(x, y, keep_sel)
		
	def set_sel(self, x, y):
		self.textedit._textedit.set_sel(x, y)


class zoidapp(zapp.zapp):
	def __init__(self):
		super().__init__()
		self.documents = []
		self.listwidth = 8
		self.searchheight = 7
		self.highlighters = {}
		
		
		self.color_modes = [(zutils.CL_WHITE, zutils.CL_BLACK), (zutils.CL_BLACK, zutils.CL_WHITE), (zutils.CL_GREEN, zutils.CL_BLACK)]
		self.color_mode = 0
		zutils.CL_FG = self.color_modes[self.color_mode][0]
		zutils.CL_BG = self.color_modes[self.color_mode][1]
		
	def load_highlighters(self):
		self.highlighters[""] = zregexhighlighter.zregexhighlighter()
		
		for i in zhighlighterlist.get_list():
			hl = zregexhighlighter.zregexhighlighter()
			try:
				hl.load_rules(i)
				for ext in hl.extensions:
					zutils.debug("Loaded highlighter for "+ext+" files")
					self.highlighters[ext] = hl
			except Exception as e:
				zutils.debug("Failed to open rule file "+i+ ": "+str(e))
		
	
	def get_current_doc(self):
		r = self.listbox._row
		
		return self.documents[r]
	
	def signal_handler(self, signal, frame):
		#print('You pressed Ctrl+C!')
		#print( "test")
		self.unget_char(zutils.KEY_VT)
		#sys.exit(0)
	
	def _on_caption_changed(self, sender):
		self.rebuild_list()
	
	def _on_switch(self, sender):
		self.documents[sender._row].set_visible(True)
		for i in range(len(self.documents)):
			if i != sender._row:
				self.documents[i].set_visible(False)
			
	
	def rebuild_list(self):
		if self.listbox._row >= len(self.documents):
			self.listbox._row=0
		
		names = []
		for doc in self.documents:
			names.append( doc.get_caption())
		self.listbox._rows = names
	
	def switch_to_document(self, document):
		i = self.documents.index(document)
		
		self.listbox._row = i
		
		self.documents[self.listbox._row].set_visible(True)
		for j in range(len(self.documents)):
			if j != i:
				self.documents[j].set_visible(False)
	
	def new_document(self):
		doc = document(self.textframe)
		doc.on_caption_change = self._on_caption_changed
		self.documents.append( doc )
		self.rebuild_list()
		return doc
	
	def save_current_document(self):
		r = self.listbox._row
		
		curr_doc = self.documents[r]
		#fn, c = zquerybox.query(self, "Save", "Filename (ESC to cancel)", curr_doc._filename)
		#if fn != None:
		#	curr_doc.save_to_file(fn)
		#	self.check_for_highlighter(curr_doc)
		folder = os.getcwd() + "/"
		if curr_doc._filename != "":
			folder = os.path.abspath(curr_doc._filename)
		
		fn = zfilebrowser.query(self, "Save file", folder, False, True)
		if fn == None:
			return False
		
		try:
			curr_doc.save_to_file(fn)
		except Exception as e:
			zmessagebox.query(self, "Error saving file!", str(e))
			return False
		
		
		self.check_for_highlighter(curr_doc)
		
		return True
	
	def check_for_highlighter(self, document):
		fn = document._filename
		_, fext = os.path.splitext(fn)
		found = False
		if fext.startswith("."):
			fext = fext[1:]
			if fext in self.highlighters:
				found = True
				document.textedit._textedit.highlighter = self.highlighters[fext]
		if not found and "default" in self.highlighters:
			document.textedit._textedit.highlighter = self.highlighters["default"]
	
	def close_document(self, d):
		r = self.documents.index(d)
		
		curr_doc = self.documents[r]
		if curr_doc.get_changed():
			btn = zmessagebox.query(self, "Save?", "Save file before closing?", ["Save", "Discard", "Cancel"])
			
			ret = True
			if btn == 0:
				ret = self.save_current_document()
			
			if btn == 2 or not ret:
				return
			
		
		self.documents.pop(r)
		#self.textframe.remove_child(curr_doc)
		self.textframe.remove_child(curr_doc.textedit)
		
		#del curr_doc
		
		r = max(0, r-1)
		
		self.rebuild_list()
		self.listbox.set_row(r)
		#close doc
	
	def close_current_document(self):
		r = self.listbox._row
		
		self.close_document(self.documents[r])
		
		
	def open_document(self):
		r = self.listbox._row
		
		curr_doc = self.documents[r]
		folder = os.getcwd() + "/"
		if curr_doc._filename != "":
			folder = os.path.dirname(os.path.abspath(curr_doc._filename)) + "/"
		
		fn = zfilebrowser.query(self, "Open file", folder, False, True)
		if fn == None:
			return False
		
		zutils.debug("Opening file "+fn)
		d = self.new_document()
		
		try:
			d.load_from_file(fn)
		except Exception as e:
			zmessagebox.query(self, "Error opening file!", str(e))
			self.close_document(d)
			return False
		
		self.check_for_highlighter(d)
		
		self.switch_to_document(d)
		return True
	
	def execute(self, executer):
		r = self.listbox._row
		
		lines = self.documents[r].get_lines()
		
		for l in lines:
			if l.startswith("#!"+executer):
				cmd = l[len("#!"+executer)+1:]
				cmd = cmd.replace("%s", self.documents[r]._filename)
				cmd = "$TERM -hold -e \""+cmd+"\""
				zutils.debug(repr(cmd))
				subprocess.Popen(cmd, shell = True)
				return
	
	def resize_textframe(self, size):
		for c in self.textframe._children:
			c.resize( size )
	
	def toggle_searchbar(self, visible):
		r = self._root_frame
		
		if visible:
			self.searchframe.set_visible(True)
			self.resize_textframe( (r._size[0] - self.listwidth, r._size[1] - self.searchheight) )
			self._root_frame.set_focus(self.searchframe)
		else:
			self.searchframe.set_visible(False)
			self.resize_textframe( (r._size[0] - self.listwidth, r._size[1]) )
			self._root_frame.set_focus(self.textframe)
	
	def show_help(self):
		helptext = """Close:    Ctrl+W       Select: (Ctrl+)Shift+Arrows
Save:     Ctrl+D       Copy:   Ctrl+C
New:      Ctrl+N       Cut:    Ctrl+X
Open:     Ctrl+O       Paste:  Ctrl+V
Search:   Ctrl+F       Run:    Ctrl+R
"""
		ztextbox.query(self, "Help", helptext, True)
	
	def do_run(self):
		zutils.load_clipboard()
		self.load_highlighters()
		signal.signal(signal.SIGINT, self.signal_handler)
		
		#zutils.CL_FG = zutils.CL_BLUE
		#zutils.CL_BG = zutils.CL_YELLOW
		
		
		r = self._root_frame
		r.set_catch_focus(True)
		
		self.textframe = zframe.zframe(r, (self.listwidth, 0), (r._size[0]-self.listwidth, r._size[1]))
		self.textframe.set_catch_focus(False)
		
		r.add_child(self.textframe)
		
		self.listbox = zlistbox.zlistbox(r, (0,0), (self.listwidth,r._size[1]), [])
		self.listbox.on_change = self._on_switch
		
		r.add_child(self.listbox)
		
		self.searchframe = zsearchframe.zsearchframe(r, (self.listwidth, r._size[1] - self.searchheight), (r._size[0]-self.listwidth, self.searchheight), self)
		self.searchframe.set_visible(False)
		
		r.add_child(self.searchframe)
		
		
		if len(sys.argv) > 1:
			for i in range(1, len(sys.argv)):
				d = self.new_document()
				d.load_from_file(sys.argv[i])
				self.check_for_highlighter(d)
		else:
			self.new_document()
			
		
		self.rebuild_list()
		self.listbox.set_row(0)
		
		
		while True:
			self.render()
			c, buf = self._get_char()
			if c == zutils.KEY_CSUP:
				self.listbox.set_row( self.listbox._row - 1)
			elif c == zutils.KEY_CSDOWN:
				self.listbox.set_row( self.listbox._row + 1)
			#elif c == zutils.KEY_VT: #Ctrl+C
			#	break
			elif c == zutils.KEY_CW:
				self.close_current_document()
				if len(self.documents) == 0:
					break
			elif c == zutils.KEY_CD:
				self.save_current_document()
			elif c == zutils.KEY_CO:
				self.open_document()
			elif c == zutils.KEY_CN:
				self.new_document()
				self.listbox.set_row(len(self.documents)-1)
			elif c == zutils.KEY_CF:
				self.toggle_searchbar(not self.searchframe.is_visible())
			elif c == zutils.KEY_CR:
				self.execute("run")
			elif c == zutils.KEY_F1:
				self.show_help()
			elif c == zutils.KEY_F2:
				self.color_mode += 1
				if self.color_mode >= len(self.color_modes):
					self.color_mode = 0
				zutils.CL_FG = self.color_modes[self.color_mode][0]
				zutils.CL_BG = self.color_modes[self.color_mode][1]
				
			zutils.debug("KEY: "+str(c))
			
			
			self._root_frame.on_key(c, buf)


app = zoidapp()
app.run()
