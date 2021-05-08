import zobj
import zwall
import zutils


class zlabel(zobj.zobj):
	def __init__(self, parent, pos=(0,0), size=(0,0), caption=""):
		super().__init__(parent, pos, size)
		self._caption = caption
		self._fcolor = None
		self._bcolor = None
		self._attr = 0
	
	def set_caption(self, caption):
		self._caption = caption
	
	def get_caption(self):
		return self._caption
	
	def set_fcolor(self, fcolor):
		self._fcolor = fcolor
	def set_bcolor(self, bcolor):
		self._bcolor = bcolor
	def set_attr(self, attr):
		self._attr = attr
	def get_fcolor(self):
		return zutils.CL_FG if self._fcolor == None else self._fcolor
	def get_bcolor(self):
		return zutils.CL_BG if self._bcolor == None else self._bcolor
	def get_attr(self):
		return self._attr
	
	
	def do_paint(self, wall):
		fc = zutils.CL_FG if self._fcolor == None else self._fcolor
		bc = zutils.CL_BG if self._bcolor == None else self._bcolor
		wall.write_text(0,0,self._caption, fc, bc, self._attr)
