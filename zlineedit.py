import zobj
import zwall
import zutils


class zlineedit(zobj.zobj):
	ch_left  = ["⌊", "⌊"]
	ch_right = ["⌉", "⌉"]
	
	def __init__(self, parent, pos=(0,0), size=(0,0), text=""):
		super().__init__(parent, pos, size)
		self.set_text(text)
		self.on_enter = None
		self.on_change = None
	
	def set_text(self, text):
		self._text = text
		self._cursor = len(self._text)
		self._left = 0
	
	def get_text(self):
		return self._text
	
	def do_paint(self, wall):
		ox = wall._offset[0]
		oy = wall._offset[1]
		
		foc = 1 if self.is_focused() else 0
		
		if(self._size[0] < 4): # are you kidding me?
			return
		for x in range(self._size[0]):
			wall.get_wall()[oy][ox+x].attr = zutils.AT_REVERSE

		textw = self._size[0]-2
		
		if(self._cursor < self._left):
			self._left = self._cursor
		elif(self._cursor > self._left + textw):
			self._left = self._cursor - textw
		
		if(self._left > 0):
			wall.get_wall()[oy][ox].c = "…"
		else:
			wall.get_wall()[oy][ox].c = self.ch_left[foc]
		
		if(len(self._text) - self._left > textw):
			wall.get_wall()[oy][ox+self._size[0]-1].c = "…"
		else:
			wall.get_wall()[oy][ox+self._size[0]-1].c = self.ch_right[foc]
			

		textp = self._left
		for x in range(1, self._size[0]-1):
			if textp >= len(self._text):
				c = " "
			else:
				c = self._text[textp]
			wall.get_wall()[oy][ox+x].c = c
			textp += 1
		self._caret = (self._cursor - self._left+1, 0)
	
	def on_key(self, key, char):
		changed = False
		if(key == zutils.KEY_LEFT and self._cursor > 0):
			self._cursor -= 1
		elif(key == zutils.KEY_RIGHT and self._cursor < len(self._text)):
			self._cursor += 1
		elif(key == zutils.KEY_END):
			self._cursor = len(self._text)
		elif(key == zutils.KEY_HOME):
			self._cursor = 0
		elif(key == zutils.KEY_DEL):
			self._text = self._text[:self._cursor] + self._text[self._cursor+1:]
			changed = True
		elif(key == zutils.KEY_BACKSPACE and self._cursor > 0):
			self._text = self._text[:self._cursor-1] + self._text[self._cursor:]
			self._cursor -= 1
			changed = True
		elif(not zutils.is_control(key) and zutils.is_printable(char) and not key == zutils.KEY_RETURN):
			self._text = self._text[:self._cursor] + char + self._text[self._cursor:]
			self._cursor += len(char)
			changed = True
		elif(key == zutils.KEY_RETURN):
			if(self.on_enter != None):
				self.on_enter(self)
		
		if(changed and self.on_change != None):
			self.on_change(self)
	
	