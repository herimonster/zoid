import zframe
import zlabel
import zlineedit
import zwall
import zutils
import ztable
import zborderframe

import os
from datetime import datetime

class zfilebrowser(zframe.zframe):
	def __init__(self, parent, pos=(0,0), size=(0,0), filename="/", select_directories = True, select_files = True):
		super().__init__(parent, pos, size)
		
		self.on_file_select = None
		self.select_directories = select_directories
		self.select_files = select_files
		
		self._sort_by = 0
		
		
		self._dirlabel = zlabel.zlabel(self, (0,0), (self._size[0], 1), "")
		self._dirlabel._wants_focus = False
		self._name = zlineedit.zlineedit(self, (0,1), (self._size[0], 1), os.path.basename(filename))
		self._name.on_enter = self._file_select
		self._table = ztable.ztable(self, (0, 3), (self._size[0], self._size[1]-3), 3)
		self._table.head = [{"caption": "Name", "width": self._table._size[0]-21, "align": ztable.ztable.AL_LEFT},
		                    {"caption": "Size", "width": 10, "align": ztable.ztable.AL_RIGHT},
		                    {"caption": "Date", "width": 10, "align": ztable.ztable.AL_LEFT}]
		 
		
		self._table.on_select = self._table_select
		self.add_child(self._dirlabel)
		self.add_child(self._name)
		self.add_child(self._table)
		zutils.debug("Name: "+self._name.get_text())
		self.goto_dir(os.path.dirname(filename))
		
		self.set_focus(self._name)
	
	def _table_select(self, sender, row):
		dir_row = 0 if self.select_directories else -1
		up_row = 1 if self.select_directories else 0
		if self._dir == "/":
			up_row = -1
		
		if row == dir_row and self.select_directories:
			self._name.set_text(".")
			self.set_focus(self._name)
			
		elif row == up_row:
			self.goto_dir(os.path.dirname(self._dir))
		else:
			if dir_row >= 0:
				row -= 1 
			if up_row >= 0:
				row -= 1
			
			if row < len(self.thedirs):
				self.goto_dir(os.path.join(self._dir, self.thedirs[row][0]))
			else:
				row -= len(self.thedirs)
				self._name.set_text(self.thefiles[row][0])
				self.set_focus(self._name)
	def _file_select(self, sender):
		fn = self._name.get_text()
		if fn != "":
			if fn == "." and self.select_directories:
				if self.on_file_select != None:
					self.on_file_select(self, self._dir)
			elif fn == "..":
				self.goto_dir(os.path.dirname(self._dir))
				self._name.set_text("")
			elif fn != "." and self.select_files:
				fn = os.path.join(self._dir, fn)
				if self.on_file_select != None:
					self.on_file_select(self, fn)
	
	def _timestamp(self, utc):
		dt = datetime.utcfromtimestamp(utc)
		today = datetime.today()
		 
		if today.year == dt.year and today.month == dt.month and today.day == dt.day:
			s = dt.strftime("  %H:%M:%S")
		else:
			s = dt.strftime('%Y-%m-%d')
		return s
	
	def _filesize(self, num):
		for unit in ['B','K','M','G','T','P','E','Z']:
			if abs(num) < 1024.0:
				return "%3.1f %s" % (num, unit)
			num /= 1024.0
		return "%.1f%s%s" % (num, 'Yi', suffix)
	
	def set_sort_by(self, sort_by):
		if sort_by <= 2 and sort_by >= 0:
			self._sort_by = sort_by
			self.goto_dir(self._dir)
	
	def goto_dir(self, dir):
		self._dir = dir
		self._dirlabel.set_caption(dir)
		self._table.rows = []
		self._table._row = 0
		try:
			contents = os.listdir(dir)
		except:
			self.goto_dir("/")
		
		self.thedirs = []
		self.thefiles = []
		for f in contents:
			fn = os.path.join(dir, f)
			try:
				stats = os.stat(fn)
				stsize = stats.st_size
				sttime = stats.st_mtime
			except:
				stsize = 0
				sttime = 0
			if os.path.isdir(fn):
				self.thedirs.append([f, stsize, sttime])
			elif os.path.isfile(fn):
				self.thefiles.append([f, stsize, sttime])
			
			self.thedirs = sorted(self.thedirs, key=lambda x: x[self._sort_by])
			self.thefiles = sorted(self.thefiles, key=lambda x: x[self._sort_by])
		
		if self.select_directories:
			self._table.rows.append([".", "", ""])
		if self._dir != "/":
			self._table.rows.append(["..", "", ""])
			today = datetime.today()
		for d in self.thedirs:
			ts = self._timestamp(d[2])
			
			self._table.rows.append([d[0], "", ts])
		
		if self.select_files:
			for f in self.thefiles:
				ts = self._timestamp(f[2])
				size = self._filesize(f[1])
				
				self._table.rows.append([f[0], size, ts])
		
		
	def on_key(self, key, char):
		if key in [zutils.KEY_UP, zutils.KEY_DOWN, zutils.KEY_PAGEUP, zutils.KEY_PAGEDOWN]:
			if self.get_focused() == self._name:
				self.set_focus(self._table)
		elif key == zutils.KEY_ESC:
			self.on_file_select(self, None)
		elif char == ">":
			self.set_sort_by(self._sort_by + 1)
		elif char == "<":
			self.set_sort_by(self._sort_by - 1)
			
		
		super().on_key(key, char)
	
	
	def get_filename(self):
		return os.path.join(self._dir, self._name.get_text())
	
	def do_paint(self, wall):
		
		self.clear_wall(wall)
		super().do_paint(wall)

def query(parent, caption="", filename="/", select_directories = True, select_files = True):
	r = parent._root_frame
	
	w = r.get_size()[0]
	h = r.get_size()[1]
	
	wui = zborderframe.zborderframe(r, (0,0), (w,h), caption)
	
	fb = zfilebrowser(wui, (1,1), (w-2,h-2), filename, select_directories, select_files)
	
	wui.add_child(fb)
	r.add_child(wui)
	r.set_focus(wui)
	
	
	global do_exit,res,c
	res = None
	c = None
	do_exit = False
	
	
	def on_select(sender, fn):
		global do_exit,res
		
		res = fn
		
		do_exit = True
	
	fb.on_file_select = on_select
	
	while True:
		parent.render()
		
		c, buf = parent._get_char()
		
		if c == zutils.KEY_ESC:
			break
		
		#elif c == zutils.KEY_VT:
		#	break
		
		fb.on_key(c, buf)
		
		if do_exit:
			break
	
	r.remove_child(wui)
	return res
