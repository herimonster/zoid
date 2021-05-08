import zborderframe
import zlabel
import zwall
import zutils

class zmessagebox(zborderframe.zborderframe):
	def __init__(self, parent, pos=(0,0), size=(0,0), caption="", text="", buttons=["Ok"]):
		super().__init__(parent, pos, size, caption)
		
		self._caption = caption
		self._text = zlabel.zlabel(self, (2,2), (self._size[0]-4, 1), text)
		self._text._wants_focus = False
		
		self.add_child(self._text)
		
		self.buttons = []
		n = len(buttons)
		w = int((self._size[0]-4)/n)
		zutils.debug("Width: "+str(w))
		for i in range(n):
			btn = zlabel.zlabel(self, (2+i*w,4), (w, 1), buttons[i])
			
			self.buttons.append(btn)
			
			self.add_child(btn)
			
		
		
		self.select_btn(0)
	
	def _on_enter(self):
		if self.on_enter != None:
			self.on_enter()
	
	def get_text(self):
		return self._text.get_text()
	
	def do_paint(self, wall):
		self.clear_wall(wall)
		super().do_paint(wall)
	
	def select_btn(self, btn):
		if btn >= len(self.buttons):
			btn = 0
		if(btn < 0):
			btn = len(self.buttons)-1
		self.btn = btn
		self.set_focus(self.buttons[self.btn])
		for i in range(len(self.buttons)):
			self.buttons[i].set_attr(zutils.AT_NORMAL)
		
		self.buttons[self.btn].set_attr(zutils.AT_REVERSE)
	
	def on_key(self, c, buf):
		if c == zutils.KEY_LEFT:
			self.select_btn(self.btn-1)
			
		elif c == zutils.KEY_RIGHT:
			self.select_btn(self.btn+1)
		
		else:
			super().on_key(c, buf)
	
def query(parent, caption, text, buttons=["Ok"]):
	r = parent._root_frame
	
	w = r.get_size()[0]
	h = 7
	y = int(r.get_size()[1] / 2 - int((h+1)/2))
	if y < 0:
		y = 0
		h = r.get_size()[1]
	
	wui = zmessagebox(r, (0,y), (w,h), caption, text, buttons)
	r.add_child(wui)
	r.set_focus(wui)
	
	res = None
	c = None
	
	while True:
		parent.render(do_clear = False)
		c, buf = parent._get_char()
		
		if c == zutils.KEY_RETURN:
			res = wui.btn
			break
		
		#elif c == zutils.KEY_VT:
		#	break
		
		wui.on_key(c, buf)
	
	r.remove_child(wui)
	return res
