import zborderframe
import zlabel
import zcheckbox
import zlineedit
import zwall
import zutils

class findingbot:
	def __init__(self, ignore_case, is_regex, lines, cursor, search_for ):
		self.ignore_case = ignore_case
		self.is_regex = is_regex
		self.text = "\n".join(lines)
		cx = cursor[0]
		cy = cursor[1]
		self.c = 0
		y = 0
		while y < cy:
			self.c += len(lines[y])+1
			y+=1
		self.c += cx
		zutils.debug("Cursor is at "+str(self.c)+"; cursor was "+ str(cursor) + " and is now "+str(self.c_to_cursor(self.c)))
		if not is_regex:
			self.search_for = search_for.replace("\\n", "\n").replace("\\t","\t").replace("\\r", "\r").replace("\\\\", "\\")
		else:
			self.search_for = search_for
		
		if ignore_case:
			self.text = self.text.lower()
			self.search_for = self.search_for.lower()
	
	def c_to_cursor(self, c):
		cy = self.text[:c].count("\n")
		cx = len(self.text[:c]) - self.text[:c].rfind("\n") - 1
		
		return cx, cy
	
	def find_next(self):
		if not self.is_regex:
			for run in [0,1]:
				a = self.text.find(self.search_for, self.c) if run == 0 else self.text.find(self.search_for, 0, self.c)
				if a != -1:
					sx, sy = self.c_to_cursor(a)
					cx, cy = self.c_to_cursor(a+len(self.search_for))
					self.c = a
					return cx,cy,sx,sy
				zutils.debug("starting from beginning")
				
			return -1,-1,-1,-1
		else:
			return 0,0,1,0

class zsearchframe(zborderframe.zborderframe):
	def __init__(self, parent, pos=(0,0), size=(0,0), documenthandler=None):
		txtsearch = "Srch. "
		txtrepl =   "Repl. "
		txtcase =   "Match case"
		txtregex =  "Reg. Expr."
		
		super().__init__(parent, pos, size, "Search and Replace")
		self._qlbl = zlabel.zlabel(self, (1,2), (len(txtsearch), 1), txtsearch)
		self._qlbl._wants_focus = False
		self._qtext = zlineedit.zlineedit(self, (len(txtsearch)+2,2), (self._size[0]-len(txtsearch)-4, 1), "")
		self._qtext.on_enter = self._on_enter_search
		
		self.add_child(self._qtext)
		self.add_child(self._qlbl)
		
		self._rlbl = zlabel.zlabel(self, (1,3), (len(txtrepl), 1), txtrepl)
		self._rlbl._wants_focus = False
		self._rtext = zlineedit.zlineedit(self, (len(txtrepl)+2,3), (self._size[0]-len(txtrepl)-4, 1), "")
		self._rtext.on_enter = self._on_enter_replace
		
		self.add_child(self._rtext)
		self.add_child(self._rlbl)
		
		self._casecb = zcheckbox.zcheckbox(self, (1,5), (len(txtcase)+2, 1), txtcase)
		self.add_child(self._casecb)
		
		self._regexcb = zcheckbox.zcheckbox(self, (len(txtcase)+4,5), (len(txtregex)+2, 1), txtregex)
		self.add_child(self._regexcb)
		
		self._documenthandler = documenthandler
		
		
	
	def _on_enter_search(self, sender):
		doc = self._documenthandler.get_current_doc()
		txt = self._qtext.get_text()
		so = findingbot( not self._casecb.is_checked(), self._regexcb.is_checked(), doc.get_lines(), doc.get_cursor(), txt)
		x1,y1,x2,y2 = so.find_next()
		if x1 != -1 and y1 != -1 and x2 != -1 and y2 != -1:
			doc.set_cursor(x1,y1)
			doc.set_sel(x2,y2)
		else:
			zutils.debug("not found :(")
		
		
	
	def _on_enter_replace(self, sender):
		pass
	
	def get_text(self):
		return self._text.get_text()
	
	def do_paint(self, wall):
		self.clear_wall(wall)
		super().do_paint(wall)
	
	def on_key(self, key, char):
		if key == zutils.KEY_UP:
			self.next_focus(True)
		elif key == zutils.KEY_DOWN:
			self.next_focus(False)
		else:
			super().on_key(key, char)