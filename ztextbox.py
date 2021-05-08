import zborderframe
import zlabel
import zlineedit
import zwall
import zutils
import ztextedit

class ztextbox(zborderframe.zborderframe):
	def __init__(self, parent, pos=(0,0), size=(0,0), caption="", text="", readonly=False):
		super().__init__(parent, pos, size, caption)
		
		self._caption = caption
		self._text = ztextedit.ztextedit(self, (1,2), (self._size[0]-2, self._size[1]-3), text, readonly)
		
		self.add_child(self._text)
		
		self.set_focus(self._text)
	
	def _on_enter(self):
		if self.on_enter != None:
			self.on_enter()
	
	def get_text(self):
		return self._text.get_text()
	
	def do_paint(self, wall):
		self.clear_wall(wall)
		super().do_paint(wall)
	
def query(parent, caption, text, readonly = False):
	r = parent._root_frame
	
	w = r.get_size()[0]
	h = int(r.get_size()[1] / 2)
	y = int(r.get_size()[1] / 2 - int((h+1)/2))
	if y < 0:
		y = 0
		h = r.get_size()[1]
	
	wui = ztextbox(r, (0,y), (w,h), caption, text, readonly)
	r.add_child(wui)
	r.set_focus(wui)
	
	res = None
	c = None
	
	while True:
		parent.render(do_clear = False)
		c, buf = parent._get_char()
		
		if c == zutils.KEY_ESC:
			res = wui.get_text()
			break
		
		#elif c == zutils.KEY_VT:
		#	break
		
		wui.on_key(c, buf)
	
	r.remove_child(wui)
	return res, c
