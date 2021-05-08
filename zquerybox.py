import zborderframe
import zlabel
import zlineedit
import zwall
import zutils

class zquerybox(zborderframe.zborderframe):
	def __init__(self, parent, pos=(0,0), size=(0,0), caption="", query="", text=""):
		super().__init__(parent, pos, size, caption)
		self._caption = caption
		self._query = zlabel.zlabel(self, (1,2), (self._size[0]-2, 1), query)
		self._text = zlineedit.zlineedit(self, (1,4), (self._size[0]-2, 1), text)
		self._text.on_enter = self._on_enter
		self.on_enter = None
		
		self.add_child(self._text)
		self.add_child(self._query)
		
	
	def _on_enter(self):
		if self.on_enter != None:
			self.on_enter()
	
	def get_text(self):
		return self._text.get_text()
	
	def do_paint(self, wall):
		self.clear_wall(wall)
		super().do_paint(wall)
	

def query(parent, caption, query, text=""):
	r = parent._root_frame
	
	w = r.get_size()[0]
	h = 7
	y = int(r.get_size()[1] / 2 - 4)
	if y < 0:
		y = 0
		h = r.get_size()[1]
	
	wui = zquerybox(r, (0,y), (w,h), caption, query, text)
	r.add_child(wui)
	r.set_focus(wui)
	
	res = None
	c = None
	
	while True:
		parent.render(do_clear = False)
		c, buf = parent._get_char()
		
		if c == zutils.KEY_RETURN:
			res = wui.get_text()
			break
		elif c == zutils.KEY_ESC:
			break
		elif c == zutils.KEY_VT:
			break
		
		wui.on_key(c, buf)
	
	r.remove_child(wui)
	return res, c
