import zobj
import zwall
import zutils

class zlistbox(zobj.zobj):
	#ch_h = ["─", "═"]
	#ch_v = ["│", "║"]
	#ch_tl= ["┌", "╔"]
	#ch_tr= ["┐", "╗"]
	#ch_bl= ["└", "╚"]
	#ch_br= ["┘", "╝"]
	#AL_LEFT = 0
	#AL_RIGHT = 1
	#AL_CENTER = 2
	
	def __init__(self, parent, pos=(0,0), size=(0,0), rows=[]):
		super().__init__(parent, pos, size)
		self._rows = rows
		self._row = 0
		self._first = 0
		self.on_change = None
		
	
	def resort(self):
		self._rows = sorted(self.rows, key=lambda row: row[self._order_by], reverse=self._desc)
	
	def set_desc(self, desc):
		self._desc = desc
		self.resort()
		
	def get_desc(self):
		return self._desc
	
	
	def add_row(self, entry):
		self.rows.append(entry)
		self.resort()
		
	def do_paint(self, wall):
		def text(px, py, text, hl, sel):
			
			fc = bc = -1
			
			at = 0
			if(hl):
				at = zutils.AT_BOLD
			if(sel):
				at |= zutils.AT_REVERSE 
			wall.write_text(px, py, text, fc, bc, at)
			
		items = self._size[1]
		width = self._size[0]
		if(self._row < self._first):
			self._first = self._row
		elif(self._row >= self._first + items):
			self._first = self._row - items + 1
			
		for i in range(items):
			if i + self._first >= len(self._rows):
				continue
			
			t = self._rows[i + self._first]
			if len(t) > width:
				t = t[:width-1]+"…"
			
			hl = i + self._first == self._row
			if hl:
				self._caret=(0,i)
			sel = self.is_focused() and hl
			
			text(0, i, t, hl, sel)
		
	def _do_change(self):
		if self.on_change != None:
			self.on_change(self)
	def set_row(self, row):
		if row >= 0 and row < len(self._rows):
			self._row = row
			self._do_change()
	
	def on_key(self, key, char):
		if(key == zutils.KEY_UP and self._row > 0):
			self.set_row(self._row - 1)
		elif(key == zutils.KEY_DOWN and self._row < len(self._rows)-1):
			self.set_row(self._row + 1)
		elif(key == zutils.KEY_END):
			self.set_row(len(self._rows)-1)
		elif(key == zutils.KEY_HOME):
			self.set_row(0)
			
	
	