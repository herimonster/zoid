import zobj
import zwall
import zutils

class ztable(zobj.zobj):
	ch_h = ["─", "═"]
	ch_v = ["│", "║"]
	ch_tl= ["┌", "╔"]
	ch_tr= ["┐", "╗"]
	ch_bl= ["└", "╚"]
	ch_br= ["┘", "╝"]
	AL_LEFT = 0
	AL_RIGHT = 1
	AL_CENTER = 2
	
	def __init__(self, parent, pos=(0,0), size=(0,0), cols=1):
		super().__init__(parent, pos, size)
		
		
		self.on_select = None
		self.on_change = None
		self.set_cols(cols)
		
	
	def resort(self):
		self.rows = sorted(self.rows, key=lambda row: row[self._order_by], reverse=self._desc)
	
	def set_cols(self, cols):
		if(cols < 1):
			cols = 1
		self._row = 0
		self._col = 0
		self._first = 0
			
		self._cols = cols
		self.head = [{"caption": str(i), "width": int(self._size[0] / cols), "align": ztable.AL_LEFT} for i in range(cols)]
		self._order_by = 0
		self._desc = False
		self.rows = []
	
	def set_order_by(self, order_by):
		if(order_by >= self._cols):
			order_by = self._cols-1
		if(order_by < 0):
			order_by = 0;
		self._order_by = order_by
		self.resort()
		
	def get_order_by(self):
		return self._order_by
	
	def set_desc(self, desc):
		self._desc = desc
		self.resort()
		
	def get_desc(self):
		return self._desc
	
	
	def add_row(self, entry):
		if(len(entry) != self._cols):
			return
		
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
			
		def blind_text(px, py, length, hl, sel):
			s = " "*length
			text(px, py, s, hl, sel)
		
		if(self._size[0] < 2 or self._size[1] < 2):
			return
		
		items = self._size[1] - 2
		
		if(self._row < self._first):
			self._first = self._row
		elif(self._row >= self._first + items):
			self._first = self._row - items + 1
		
		
		#wall.write_text(0,0, "TEST "+str(self.head[0]["width"]), -1, -1, 0)
		style = 0
		
		
		self._caret = (0, 0)
		p = 0
		for c in range(self._cols):
			w = self.head[c]["width"]
			blind_text(p,0,w,c % 2 == 1, False)
			text(p,0, self.head[c]["caption"][:w], c % 2 == 1, False)
			p += w
		
		text(0,1,"─"*self._size[0],False,False)
		#for c in range(self._size[0]):
		#	wall.get_wall()[1][c].c = "═"
		#wall.get_wall()[1][0].c = str(items)[0]
		#wall.get_wall()[1][1].c = str(items)[1:]
		y = 2
		for r in range(self._first, min(self._first + items, len(self.rows))):
			p = 0
			sel = (r == self._row)

			for c in range(self._cols):
				w = self.head[c]["width"]
				a = self.head[c]["align"]
				if(w < 1):
					continue
				
				if(sel and c == self._col):
					self._caret = (p, y)
					
				blind_text(p,y,w,c % 2 == 1, sel)
				t = ""
				ro = str(self.rows[r][c]);
				if(a == ztable.AL_LEFT):
					t = ro[:w]
					if(len(ro) > w):
						t = t[:w-1] +  '…'
				elif(a == ztable.AL_RIGHT):
					t = ro[-w:]
					if(len(ro) > w):
						t = "…" + t[1:]
					else:
						t = (w-len(ro)-1)*" " + t
					
				text(p,y, t, c % 2 == 1, sel)
				
				p += w
			y += 1
			
	def get_row(self):
		return self._row
	
	def get_row_entry(self):
		return self.rows[self._row]
	
	def on_key(self, key, char):
		changed = False
		if(key == zutils.KEY_UP and self._row > 0):
			self._row -= 1
			changed = True
		elif(key == zutils.KEY_DOWN and self._row < len(self.rows)-1):
			self._row += 1
			changed = True
		elif(key == zutils.KEY_END):
			self._row = len(self.rows)-1
			changed = True
		elif(key == zutils.KEY_HOME):
			self._row = 0
			changed = True
		elif(key == zutils.KEY_PAGEUP):
			self._row = max(0, self._row - (self._size[1] - 3))
			changed = True
		elif(key == zutils.KEY_PAGEDOWN):
			self._row = min(len(self.rows)-1, self._row + (self._size[1] - 3))
			if self._row == -1:
				self._row = 0
			changed = True
		elif(key == zutils.KEY_RETURN):
			if self.on_select and len(self.rows) > 0:
				self.on_select(self, self._row)
		if changed and self.on_change:
			self.on_change(self, self._row)
	
